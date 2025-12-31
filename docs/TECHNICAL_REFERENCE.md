# 🛠️ NeuroShorts MVP - Technical Reference

This document provides a detailed breakdown of the project files and their specific functions. Intended for Development & Management.

## 📂 Root Directory: `ShortsYoutube/`

| File / Folder | Purpose |
| :--- | :--- |
| `NeuroShorts_MVP/` | **Main Application**. Contains the Python source code and assets. |
| `n8n/` | **Infrastructure**. Contains Docker configuration for the automation workflow. |
| `docs/` | **Documentation**. Contains guides, prompts, and this reference. |
| `EL MAPA DE SEGUIMIENTO.docx` | **Project Management**. Tracks progress and milestones (Critical File). |
| `apiGemini.txt` | **Secrets**. Stores API keys for AI services (Critical File). |

---

## 🐍 Engine Directory: `NeuroShorts_MVP/`

### `src/` (Source Code)
*   **`render_engine.py`**: The **Core**. This is the monolithic script that handles everything:
    *   **Classes**: `VideoInput` (Data Model), `RenderEngine` (Logic), `SubtitleEngine` (Text on screen).
    *   **Functions**: `process_visual_assets` (Downloads/Generates images), `run` (Orchestrates FFmpeg).
    *   **Configuration**: Contains the `NICHE_STYLES` dictionary defining fonts/music for each category.

### `assets/` (Media Resources)
*   **`Creepy/`, `History/`, etc.**: Niche-specific folders.
    *   Should contain `ambient.mp3` or specific background music tracks for that genre.
    *   Used by the engine to resolve `musica_fondo` paths.

### `temp/` (Temporary Workspace)
*   **`input.json`**: The **Bridge**. n8n writes to this file; Python reads from it.
*   **`*.jpg`, `*.mp3`, `*.ass`**: Intermediate assets generated during the render process. Can be safely cleared after rendering.

### `output/` (Final Deliverables)
*   Stores the final rendered `.mp4` videos.

### `tests/` (Verification)
*   Contains test scripts (`test_subprocess.py`) and mock data (`test_url_input.json`) used for debugging and feature verification.

### `setup/`
*   **`ffmpeg.zip`**: Archive containing the FFmpeg binaries.
*   **`requirements.txt`**: Python dependencies list.

---

## 🐳 Infrastructure: `n8n/`

*   **`docker-compose.yml`**: Defines the services:
    *   **n8n**: The workflow automation tool.
    *   **postgres**: The database backend for n8n.
    *   **Volumes**: Maps `D:/RODO/Proyectos/ShortsYoutube/NeuroShorts_MVP` to `/home/node/neuroshorts` to allow file writing.
*   **`.env`**: Configuration variables (Passwords, Timezone) for Docker.
*   **`init-data.sh`**: Initialization script for the PostgreSQL database.

---

## 📝 Integration Points

### The "Handshake" (n8n ➡️ Python)
1.  **n8n** executes a Node.js script using the `Execute Command` node.
2.  It writes a JSON string to `/home/node/neuroshorts/temp/input.json`.
3.  **Python** reads `D:\...\NeuroShorts_MVP\temp\input.json`.
4.  **Python** parses the JSON. If it finds Markdown blocks (```json), it strips them automatically.

### The "Smart Download" Protocol
*   If `path_imagen` is a URL (`http...`) -> Python downloads it using `requests`.
*   If `path_imagen` is empty but `descripcion_visual` exists -> Python calls `pollinations.ai` to generate it.
