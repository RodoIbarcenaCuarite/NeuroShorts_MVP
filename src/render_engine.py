import os
import asyncio
import json
import random
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Literal
from pathlib import Path

# Third-party imports
# Third-party imports
from pydantic import BaseModel, Field, ValidationError
import edge_tts
import requests
from PIL import Image

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================

# Using explicit path provided by user
FFMPEG_BIN = r"C:\ShortsYou\bin\ffmpeg.exe"
FFPROBE_BIN = r"C:\ShortsYou\bin\ffprobe.exe"

NICHE_STYLES = {
    "Creepy": {
        "font": "Arial",
        "font_size": 48, 
        "primary_color": "&H00FFFFFF",
        "outline_color": "&H000000FF", 
        "shadow_depth": 3,
        "bg_music_volume": 0.3,
        "video_filter": "vignette=PI/4, curves=preset=vintage",
        "voice": "es-MX-JorgeNeural" 
    },
    "WhatIf": {
        "font": "Impact",
        "font_size": 56,
        "primary_color": "&H0000FFFF", 
        "outline_color": "&H00000000", 
        "shadow_depth": 0,
        "bg_music_volume": 0.4,
        "video_filter": "eq=contrast=1.2:saturation=0.5",
        "voice": "es-ES-AlvaroNeural"
    },
    "History": {
        "font": "Times New Roman",
        "font_size": 52,
        "primary_color": "&H0000D7FF", 
        "outline_color": "&H00000000",
        "shadow_depth": 2,
        "bg_music_volume": 0.5,
        "video_filter": "colorbalance=rs=.3",
        "voice": "es-ES-ElviraNeural"
    },
    "TrueCrime": {
        "font": "Arial",
        "font_size": 48,
        "primary_color": "&H00E0E0E0", 
        "outline_color": "&H00000000",
        "shadow_depth": 0,
        "bg_music_volume": 0.3,
        "video_filter": "hue=s=0, curves=strong_contrast",
        "voice": "es-MX-DaliaNeural"
    },
    "Quiz": {
        "font": "Verdana",
        "font_size": 60,
        "primary_color": "&H00FFFFFF",
        "outline_color": "&H00000000",
        "shadow_depth": 3,
        "bg_music_volume": 0.35,
        "video_filter": "",
        "voice": "es-MX-CecilioNeural"
    },
    "Datos Perturbadores": {
        "font": "Arial",
        "font_size": 52, 
        "primary_color": "&H000000FF", # Red text
        "outline_color": "&H00FFFFFF", # White outline
        "shadow_depth": 3,
        "bg_music_volume": 0.35,
        "video_filter": "vignette=PI/4, curves=preset=strong_contrast",
        "voice": "es-MX-JorgeNeural"
    }
}

# Resolve paths relative to this script file (NeuroShorts_MVP/src/render_engine.py)
# BASE_DIR = NeuroShorts_MVP/
BASE_DIR = Path(__file__).resolve().parent.parent 

ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# ==========================================
# 2. DATA MODELS (Pydantic)
# ==========================================

class Scene(BaseModel):
    texto: str
    path_imagen: Optional[str] = None
    descripcion_visual: Optional[str] = None
    duracion_estimada: float = Field(alias="duracion", default=5.0) # Handle 'duracion' alias from n8n

class GlobalConfig(BaseModel):
    musica_fondo: Optional[str] = Field(alias="musica", default=None)
    volumen_musica: float = 0.3

class VideoInput(BaseModel):
    titulo: str
    nicho: Literal["Creepy", "WhatIf", "History", "TrueCrime", "Quiz", "Datos Perturbadores"] # Added new niche
    escenas: List[Scene]
    configuracion: GlobalConfig
    hook_visual: Optional[str] = None # Added hook_visual

# ==========================================
# 3. CORE ENGINES
# ==========================================

class VoiceGenerator:
    """Handles Text-to-Speech generation using Edge-TTS with retry logic."""
    
    @staticmethod
    async def generate_audio(text: str, voice: str, output_path: Path, rate: str = "+0%") -> str:
        """Generates mp3 file and returns the path."""
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await communicate.save(str(output_path))
                return str(output_path)
            except Exception as e:
                print(f"Update: TTS attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2)
        return ""

class SubtitleEngine:
    """Generates .ass subtitle files for FFmpeg."""
    @staticmethod
    def milliseconds_to_ass(ms):
        seconds = ms / 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        cs = int((s - int(s)) * 100)
        return f"{int(h)}:{int(m):02}:{int(s):02}.{cs:02}"

    @staticmethod
    def create_ass_file(scenes_data: List[dict], style_config: dict, output_path: Path):
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style_config['font']},{style_config['font_size']},{style_config['primary_color']},{style_config['primary_color']},{style_config['outline_color']},&H80000000,-1,0,0,0,100,100,0,0,1,1,{style_config['shadow_depth']},2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for scene in scenes_data:
            start = SubtitleEngine.milliseconds_to_ass(scene['start'] * 1000)
            end = SubtitleEngine.milliseconds_to_ass(scene['end'] * 1000)
            text = scene['text']
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(header + "\n".join(events))


class RenderEngine:
    def __init__(self, input_data: VideoInput):
        self.data = input_data
        self.style = NICHE_STYLES[input_data.nicho]
        
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def check_dependencies(self):
        try:
            print(f"Checking dependencies at: {FFMPEG_BIN}")
            subprocess.run([FFMPEG_BIN, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            subprocess.run([FFPROBE_BIN, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"❌ Error Crítico: {e}")
            raise RuntimeError(f"❌ Error Crítico: {e}")

    def _create_placeholder(self, idx: int) -> str:
        """Creates a black placeholder image if download fails."""
        try:
            path = TEMP_DIR / f"placeholder_{idx}.jpg"
            img = Image.new('RGB', (1080, 1920), color='black')
            img.save(path)
            print(f"⚠️ Created placeholder for scene {idx}")
            return str(path)
        except Exception as e:
            print(f"❌ Failed to create placeholder: {e}")
            return ""

    def process_visual_assets(self):
        """Downloads images from URLs or generates them via Pollinations with Multi-Model Fallback."""
        print("🌍 Checking for remote assets...")
        
        # Helper to download with Model Cascade
        def download_image_with_fallback(prompt: str, idx: int) -> str:
            import time
            import urllib.parse
            import random
            
            # Cascade Strategy: Try best models first, then faster ones
            models_to_try = ["flux", "turbo", None] 
            headers = {"User-Agent": "NeuroShortsMVP/1.0"}
            
            base_prompt = urllib.parse.quote(f"{prompt}, cinematic lighting, photorealistic, 8k, vertical ratio 9:16")
            
            for model in models_to_try:
                seed = random.randint(1, 99999)
                model_param = f"&model={model}" if model else ""
                url = f"https://image.pollinations.ai/prompt/{base_prompt}?width=1080&height=1920&nologo=true&seed={seed}{model_param}"
                
                print(f"  🎨 Generating Scene {idx+1} [Model: {model or 'default'}]...")
                
                try:
                    response = requests.get(url, headers=headers, timeout=45)
                    response.raise_for_status()
                    
                    # Verify it's actually an image (sometimes APIs return text errors as 200 OK)
                    if "image" not in response.headers.get("content-type", ""):
                         print(f"     ⚠️ Invalid content type: {response.headers.get('content-type')}")
                         raise ValueError("Not an image")

                    filename = f"scene_{idx}_visual.jpg"
                    local_path = TEMP_DIR / filename
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    
                    # Double check image validity
                    try:
                        with Image.open(local_path) as img:
                            img.verify()
                        print(f"     ✅ Saved (Variant: {model}): {filename}")
                        return str(local_path.resolve())
                    except:
                        print("     ⚠️ Image file corrupted. Retrying...")
                        
                except Exception as e:
                    print(f"     ⚠️ Model '{model}' failed: {e}")
                    time.sleep(1) # Brief pause before next model
            
            # If all models fail
            print(f"     ❌ All image models failed for Scene {idx+1}.")
            return self._create_placeholder(idx)

        # Helper for direct URL download
        def download_direct_url(url: str, idx: int) -> str:
             try:
                 print(f"  ⬇️ Downloading direct URL for Scene {idx+1}...")
                 headers = {"User-Agent": "NeuroShortsMVP/1.0"}
                 response = requests.get(url, headers=headers, timeout=30)
                 response.raise_for_status()
                 filename = f"scene_{idx}_visual.jpg"
                 local_path = TEMP_DIR / filename
                 with open(local_path, "wb") as f:
                     f.write(response.content)
                 return str(local_path.resolve())
             except Exception as e:
                 print(f"     ❌ Download failed: {e}")
                 return self._create_placeholder(idx)

        for idx, scene in enumerate(self.data.escenas):
            # Case A: We have a direct URL
            if scene.path_imagen and scene.path_imagen.strip().lower().startswith("http"):
                scene.path_imagen = download_direct_url(scene.path_imagen, idx)
                
            # Case B: We have a description but NO URL -> Use Pollinations Strategy
            elif not scene.path_imagen and scene.descripcion_visual:
                scene.path_imagen = download_image_with_fallback(scene.descripcion_visual, idx)
            
            # Case C: Local path
            elif scene.path_imagen and os.path.exists(scene.path_imagen):
                pass
            
            # Case D: Nothing -> Placeholder
            else:
                 print(f"⚠️ No visual data for Scene {idx}. Using placeholder.")
                 scene.path_imagen = self._create_placeholder(idx)

    async def run(self):
        # Pre-process: Download assets
        self.process_visual_assets()

        print(f"🎬 Starting render for: {self.data.titulo} ({self.data.nicho})")
        
        # =========================================================================
        # ⚡ SAFETY CHECK: DURATION ENFORCEMENT (58s Limit)
        # =========================================================================
        print("⏱️ Checking estimated duration...")
        temp_audios = []
        total_duration = 0.0
        
        # 1. Generate preliminary audios to measure length
        for idx, scene in enumerate(self.data.escenas):
            temp_path = TEMP_DIR / f"pre_calc_{idx}.mp3"
            await VoiceGenerator.generate_audio(scene.texto, self.style['voice'], temp_path)
            dur = self.get_audio_duration(temp_path)
            total_duration += (dur + 0.2) # Add padding used in render logic
            temp_audios.append(temp_path)
            
        print(f"   Original Estimated Total Duration: {total_duration:.2f}s")
        
        # 2. Calculate Speed Factor if needed
        audio_rate = "+0%"
        MAX_DURATION = 59.0
        TARGET_DURATION = 58.0
        
        if total_duration > MAX_DURATION:
            ratio = total_duration / TARGET_DURATION
            percent_speedup = int((ratio - 1) * 100)
            
            # Cap at +25% to avoid chipmunk effect
            if percent_speedup > 25: 
                print(f"⚠️ WARNING: Script is WAY too long ({total_duration}s). Speeding up by Max 25%.")
                percent_speedup = 25
            
            audio_rate = f"+{percent_speedup}%"
            print(f"🚨 DURATION LIMIT EXCEEDED. Applying 'Speed Up' Safety Protocol.")
            print(f"   🚀 Acceleration Rate: {audio_rate} (Target: ~{TARGET_DURATION}s)")
        else:
             print("✅ Duration is within safe limits (Youtube Shorts < 60s).")

        # Clean up pre-calc files
        for p in temp_audios:
            if p.exists(): os.remove(p)

        # =========================================================================
        # END SAFETY CHECK
        # =========================================================================

        current_time = 0.0
        audio_segments = []
        ass_events_data = []
        video_inputs = []
        
        for idx, scene in enumerate(self.data.escenas):
            print(f"  > Processing Scene {idx+1}...")
            
            # A. Generate Audio (With potentially modified rate)
            audio_path = TEMP_DIR / f"scene_{idx}.mp3"
            await VoiceGenerator.generate_audio(scene.texto, self.style['voice'], audio_path, rate=audio_rate)
            
            # Get Duration
            duration = self.get_audio_duration(audio_path) + 0.2
            audio_segments.append(str(audio_path))
            
            # B. Prepare Subtitle Data (Per Scene)
            scene_ass_path = TEMP_DIR / f"scene_{idx}.ass"
            # Single event for this scene (start at 0.0 relative to scene)
            scene_events = [{
                "start": 0.0,
                "end": duration,
                "text": scene.texto.replace("\n", " ")
            }]
            SubtitleEngine.create_ass_file(scene_events, self.style, scene_ass_path)
            
            video_inputs.append(scene.path_imagen)
            
            # Ken Burns / Visual Effects
            frames = int(duration * 30)
            zoom_cmd = f"zoompan=z='min(zoom+0.0015,1.5)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
            if self.style.get('video_filter'):
                zoom_cmd += f",{self.style['video_filter']}"
            
            # Add Subtitles to video filter chain
            # Escape path for filter
            scene_ass_path_str = str(scene_ass_path).replace("\\", "/").replace(":", "\\:")
            zoom_cmd += f",ass='{scene_ass_path_str}'"
            
            # Render Scene
            await self.render_scene_segment(idx, scene.path_imagen, str(audio_path), duration, zoom_cmd)
            current_time += duration

        # 2. Concat Segments
        concat_list_path = TEMP_DIR / "concat_list.txt"
        with open(concat_list_path, "w") as f:
            for idx in range(len(self.data.escenas)):
                f.write(f"file 'scene_{idx}_out.mp4'\n")

        # 4. Final Merge (Two-Pass Strategy for Stability)
        print("Running Pass 1: Concatenation...")
        intermediate_file = TEMP_DIR / "intermediate_concat.mp4"
        
        # Pass 1: Simple Concat of scenes (Video + Voice + Subtitles)
        concat_cmd = [
            FFMPEG_BIN, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
            "-c", "copy",
            str(intermediate_file)
        ]
        
        try:
            subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Pass 1 (Concat) Failed:\n{e.stderr}")
            raise e

        # Pass 2: Audio Mixing
        print("Running Pass 2: Audio Mixing...")
        # Sanitize Title for Filename
        import re
        safe_title = re.sub(r'[<>:"/\\|?*]', '', self.data.titulo) # Remove Window forbidden chars
        safe_title = safe_title.replace(' ', '_')
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"{safe_title}_{timestamp}.mp4"
        
        final_cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(intermediate_file) # Input 0: Video+Voice
        ]
        
        # Resolve Music Path (Handle relative paths from ASSETS_DIR or Niche folder)
        music_path = None
        if self.data.configuracion.musica_fondo:
            candidates = [
                Path(self.data.configuracion.musica_fondo), # As is (absolute)
                ASSETS_DIR / self.data.configuracion.musica_fondo, # In assets root
                ASSETS_DIR / self.data.nicho / self.data.configuracion.musica_fondo # In niche folder
            ]
        if self.data.configuracion.musica_fondo:
            # 1. Direct Candidates
            candidates = [
                Path(self.data.configuracion.musica_fondo), # Absolute
                ASSETS_DIR / self.data.configuracion.musica_fondo, # Assets root
                ASSETS_DIR / self.data.nicho / self.data.configuracion.musica_fondo, # Niche folder
            ]
            
            # 2. Search recursively in assets if not found
            if not any(c.exists() for c in candidates):
                print(f"🔍 Searching for '{self.data.configuracion.musica_fondo}' in {ASSETS_DIR}...")
                found = list(ASSETS_DIR.rglob(self.data.configuracion.musica_fondo))
                if found:
                    candidates.append(found[0])
            
            for c in candidates:
                if c.exists():
                    music_path = c
                    break
            
            if not music_path:
                print(f"⚠️ Music file '{self.data.configuracion.musica_fondo}' NOT FOUND.")
                print("   Listing available mp3 files in assets:")
                available_music = list(ASSETS_DIR.rglob("*.mp3"))
                for m in available_music[:5]: # Show first 5
                    print(f"   - {m.name}")
                
                # FALLBACK: Use first available music if any exist
                if available_music:
                    music_path = available_music[0]
                    print(f"🎵 Fallback: Using '{music_path.name}' instead.")

        if music_path:
            # Pass 2: Audio Mixing (AUDIO ONLY - Safer)
            print(f"Running Pass 2: Audio Mixing (Music: {music_path.name})...")
            mixed_audio_file = TEMP_DIR / "final_mixed_audio.aac"
            
            # [1:a]volume...[bg];[0:a][bg]amix...
            filter_complex = f"[1:a]volume={self.style['bg_music_volume']}[bg];[0:a][bg]amix=inputs=2:duration=first[a_out]"
            
            audio_mix_cmd = [
                FFMPEG_BIN, "-y",
                "-i", str(intermediate_file), # Input 0
                "-stream_loop", "-1", "-i", str(music_path), # Input 1
                "-filter_complex", filter_complex,
                "-map", "[a_out]",
                "-vn", # No Video
                "-c:a", "aac", "-b:a", "192k",
                str(mixed_audio_file)
            ]
            
            try:
                subprocess.run(audio_mix_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=TEMP_DIR)
            except subprocess.CalledProcessError as e:
                print(f"❌ Pass 2 (Audio Mix) Failed. Disabling music for this render.\n{e.stderr}")
                # Fallback: Just use audio from intermediate
                mixed_audio_file = None

            # Pass 3: Final Mux (Video Copy + New Audio)
            print("Running Pass 3: Final Muxing...")
            final_cmd = [
                FFMPEG_BIN, "-y",
                "-i", str(intermediate_file),
            ]
            
            if mixed_audio_file and os.path.exists(mixed_audio_file):
                final_cmd.extend([
                     "-i", str(mixed_audio_file),
                     "-map", "0:v", "-map", "1:a", # Map Video from 0, Audio from 1
                     "-c", "copy",
                     "-shortest"
                ])
            else:
                 final_cmd.extend([
                     "-c", "copy"
                ])
            
            final_cmd.append(str(output_file))
            
        else:
            # No music, just copy intermediate to final
            final_cmd = [
                FFMPEG_BIN, "-y",
                "-i", str(intermediate_file),
                "-c", "copy",
                str(output_file)
            ]

        try:
            subprocess.run(final_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=TEMP_DIR)
            print(f"✅ Video created: {output_file}")
            
            # Cleanup intermediate
            if os.path.exists(intermediate_file):
                os.remove(intermediate_file)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Pass 3 (Mux) Failed:\n{e.stderr}")
            raise e


    def get_audio_duration(self, path):
        try:
            result = subprocess.run(
                [FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            return 5.0 

    async def render_scene_segment(self, idx, image_path, audio_path, duration, zoom_cmd):
        out_name = TEMP_DIR / f"scene_{idx}_out.mp4"
        cmd = [
            FFMPEG_BIN, "-y",
            "-loop", "1", "-t", str(duration), "-i", image_path,
            "-i", audio_path,
        ]
        
        if zoom_cmd:
            cmd.extend(["-vf", zoom_cmd])
            
        cmd.extend([
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", "-c:a", "aac",
            "-shortest", 
            str(out_name)
        ])
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg Error in Scene {idx}:\n{e.stderr}")
            raise e

# ==========================================
# 4. ENTRY POINT
# ==========================================

async def main(json_path: str):
    print(f"🔧 Inicializando Motor de Renderizado...")
    
    # 1. Read Raw File
    with open(json_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Extract JSON from potential wrappers (Gemini Raw, Markdown, etc)
    import re
    
    # Try parsing as JSON first
    try:
        raw_data = json.loads(content)
        
        # Case A: Gemini Raw Response (parts[0].text)
        if isinstance(raw_data, dict) and "parts" in raw_data:
             print("⚠️ Detected Raw Gemini Response. Extracting content...")
             content = raw_data["parts"][0]["text"]
        elif isinstance(raw_data, dict) and "candidates" in raw_data: # Another Gemini format
             content = raw_data["candidates"][0]["content"]["parts"][0]["text"]
             
    except json.JSONDecodeError:
        print("⚠️ Direct JSON parse failed. Trying to sanitize content...")
        # Fallback for "Invalid escape" issues (common with shell echo)
        try:
            # 1. Unescape strict backslashes that might have been doubled
            sanitized = content.encode('utf-8').decode('unicode_escape')
            raw_data = json.loads(sanitized)
        except:
             try:
                 # 2. Manual regex replace of bad escapes
                 import re
                 sanitized = re.sub(r'\\([^"\\/bfnrtu])', r'\1', content)
                 raw_data = json.loads(sanitized)
             except:
                 pass # Let the next steps handle it or fail later
        
    # 3. Clean Markdown (```json ... ```)
    # Regex to find the first JSON-like block { ... } or [ ... ]
    # We look for a block strictly starting with { or [ and ending with } or ]
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
    if json_match:
        print("🧹 Cleaning Markdown code blocks...")
        content_to_parse = json_match.group(1)
    else:
        # Fallback: Find first { or [
        match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', content)
        if match:
             content_to_parse = match.group(1)
        else:
             content_to_parse = content

    # 4. Final Parse
    try:
        final_data = json.loads(content_to_parse)
        
        # Case B: It's a list [ { ... } ] -> Take first item
        if isinstance(final_data, list):
            print("⚠️ Input is a list. Using first item.")
            final_data = final_data[0]
            
        if "error" in final_data:
             print(f"❌ Error recibido desde n8n: {final_data['error']}")
             print(f"   Detalles: {final_data.get('details', 'N/A')}")
             return

        video_input = VideoInput(**final_data)
        engine = RenderEngine(video_input)
        engine.check_dependencies()
        await engine.run()
        
    except Exception as e:
        print(f"❌ Error procesando el JSON de entrada: {e}")
        print(f"Raw Content start: {content[:200]}...")
        import traceback
        traceback.print_exc()
        print(f"❌ Error inesperado: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python render_engine.py <input.json>")
    else:
        asyncio.run(main(sys.argv[1]))
