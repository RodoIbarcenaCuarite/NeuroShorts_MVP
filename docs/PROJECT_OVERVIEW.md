# 🎬 NeuroShorts MVP - Project Overview

## 🧠 What is this?
**NeuroShorts** is an automated video generation pipeline designed to create high-quality YouTube Shorts, TikToks, and Reels based on specific "Niches" (e.g., Creepy, Curiosities, History).

It combines **n8n** (for workflow automation and content generation with AI) with a custom **Python Render Engine** (for professional video assembly).

## 🚀 How it Works (The Flow)

### 1. The Brain (n8n & AI)
*   **n8n** runs in a Docker container.
*   It uses AI (Gemini/OpenAI) to generate a script, visual descriptions, and specific "Niche" styles based on a topic.
*   **Output**: It generates a structured JSON file containing all the video metadata (Script, Scenes, Prompts).
*   **Transfer**: This JSON is saved directly to `NeuroShorts_MVP/temp/input.json` via a shared Docker Volume.

### 2. The Engine (Python)
*   The `render_engine.py` script detects the input file.
*   **Smart Assets**:
    *   **Images**: It checks if the JSON has URLs. If yes, it downloads them. If NO (or if they fail), it uses **Pollinations AI** to generate images on the fly based on the visual descriptions.
    *   **Audio**: It generates Voiceovers (TTS) using Edge-TTS (Microsoft Azure tech).
    *   **Music**: It selects the correct background atmosphere based on the Niche.
*   **Assembly**:
    *   It uses **FFmpeg** (the industry standard for video) to stitch everything together.
    *   It applies automated subtitles (burned-in) with specific fonts/colors per niche.
    *   It mixes audio automatically.

### 3. The Result
*   A polished `.mp4` video is saved in the `NeuroShorts_MVP/output` folder.
*   The filename is sanitized and stamped with the date/time (e.g., `El_Monstruo_Interno_20251226.mp4`).

---

## ✨ Key Features
*   **Smart Download**: Handles both direct URLs and Text Prompts (auto-generation).
*   **Fault Tolerance**: If an image fails to download, the system doesn't crash; it generates a fallback or placeholder to ensure the video is delivered.
*   **Niche Styling**: The engine knows that a "Creepy" video needs a different font and music than a "Quiz" video.
*   **Docker Integration**: Seamless file sharing between the containerized AI world and the local Windows Media world.
