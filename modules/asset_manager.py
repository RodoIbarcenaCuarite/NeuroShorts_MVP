import os
import json
import time
import requests
from pathlib import Path
from PIL import Image

# Reutilizamos constantes o lógica si es necesario
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

def check_and_download_assets(weekly_folder: Path):
    """
    Recorre los proyectos de la semana y asegura que tengan assets.
    """
    print(f"🔍 [Assets] Escaneando: {weekly_folder.name}")
    
    for project_dir in weekly_folder.iterdir():
        if not project_dir.is_dir(): continue
        
        metadata_path = project_dir / "metadata.json"
        guion_path = project_dir / "guion.json"
        assets_dir = project_dir / "assets"
        
        if not metadata_path.exists() or not guion_path.exists():
            print(f"⚠️ [Skip] Carpeta inválida: {project_dir.name}")
            continue
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        if metadata.get("status") == "READY":
            continue # Ya está listo
            
        print(f"🔧 [Processing] {project_dir.name}")
        
        if not assets_dir.exists():
            assets_dir.mkdir()

        with open(guion_path, "r", encoding="utf-8") as f:
            guion = json.load(f)

        # 1. IMÁGENES
        all_images_ok = True
        for idx, escena in enumerate(guion.get("escenas", [])):
            img_path = assets_dir / f"scene_{idx}.jpg"
            
            if img_path.exists():
                continue # Ya la tenemos
            
            print(f"  ⬇️ Descargando Escena {idx+1}...")
            # Lógica de descarga robusta (Flux -> Turbo -> Fallback)
            success = _download_image_robust(escena.get("descripcion_visual"), img_path)
            if not success:
                print(f"  ❌ Fallo descarga Escena {idx+1}")
                all_images_ok = False
        
        # 2. AUDIO (Placeholder - aquí iría la generación con EdgeTTS)
        # Por ahora asumimos que el Render Engine hace el TTS, o lo movemos aquí.
        # Para el MVP Factory, dejemos que render_engine haga el TTS para no duplicar todo hoy.
        
        # 3. ACTUALIZAR ESTADO Y GUION
        if all_images_ok:
            # Actualizar paths en el guion para que el Render Engine use los archivos locales
            for idx, escena in enumerate(guion.get("escenas", [])):
                img_path = assets_dir / f"scene_{idx}.jpg"
                if img_path.exists():
                    escena["path_imagen"] = str(img_path.resolve())
            
            # Guardar guion actualizado
            with open(guion_path, "w", encoding="utf-8") as f:
                json.dump(guion, f, indent=2, ensure_ascii=False)

            metadata["status"] = "READY"
            print(f"✅ [Ready] Proyecto completado y guion actualizado: {project_dir.name}")
        else:
            metadata["status"] = "MISSING_ASSETS"
            print(f"⚠️ [Incomplete] Faltan archivos en: {project_dir.name}")
            
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

def _download_image_robust(prompt, target_path):
    """Versión simplificada de la lógica Multi-Modelo"""
    import urllib.parse
    import random
    
    if not prompt: return False
    
    models = ["flux", "turbo", None]
    base_prompt = urllib.parse.quote(f"{prompt}, cinematic lighting, 8k, vertical 9:16")
    
    for model in models:
        try:
            seed = random.randint(1, 99999)
            model_param = f"&model={model}" if model else ""
            url = f"https://image.pollinations.ai/prompt/{base_prompt}?width=1080&height=1920&nologo=true&seed={seed}{model_param}"
            
            resp = requests.get(url, timeout=45)
            # Validar que no sea el PNG de "Rate Limit Reached" (Suele ser pequeño < 10KB)
            if len(resp.content) < 15000: # 15KB threshold
                print("  ⚠️ [Rate Limit?] Imagen sospechosamente pequeña. Reintentando...")
                time.sleep(10)
                continue
                    
            with open(target_path, "wb") as f:
                f.write(resp.content)
            
            print("  ✅ Imagen guardada.")
            time.sleep(10) # 10s de paciencia para calidad (según solicitud usuario)
            return True
        except:
            time.sleep(2) # Pausa por error
    
    return False

if __name__ == "__main__":
    # Test manual
    pass
