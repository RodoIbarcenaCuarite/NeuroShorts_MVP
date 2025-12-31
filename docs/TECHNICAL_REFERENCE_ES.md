# 🛠️ NeuroShorts MVP - Referencia Técnica

Este documento proporciona un desglose detallado de los archivos del proyecto y sus funciones específicas. Destinado a Desarrollo y Gestión.

## 📂 Directorio Raíz: `ShortsYoutube/`

| Archivo / Carpeta | Propósito |
| :--- | :--- |
| `NeuroShorts_MVP/` | **Aplicación Principal**. Contiene el código fuente Python y los activos. |
| `n8n/` | **Infraestructura**. Contiene la configuración Docker para el flujo de automatización. |
| `docs/` | **Documentación**. Contiene guías, prompts y esta referencia. |
| `EL MAPA DE SEGUIMIENTO.docx` | **Gestión de Proyecto**. Rastrea progreso e hitos (Archivo Crítico). |
| `apiGemini.txt` | **Secretos**. Almacena claves API para servicios de IA (Archivo Crítico). |

---

## 🐍 Directorio del Motor: `NeuroShorts_MVP/`

### `src/` (Código Fuente)
*   **`render_engine.py`**: El **Núcleo**. Este es el script monolítico que maneja todo:
    *   **Clases**: `VideoInput` (Modelo de Datos), `RenderEngine` (Lógica), `SubtitleEngine` (Texto en pantalla).
    *   **Funciones**: `process_visual_assets` (Descarga/Genera imágenes), `run` (Orquestra FFmpeg).
    *   **Configuración**: Contiene el diccionario `NICHE_STYLES` definiendo fuentes/música para cada categoría.

### `assets/` (Recursos Multimedia)
*   **`Creepy/`, `History/`, etc.**: Carpetas específicas por nicho.
    *   Deben contener `ambient.mp3` o pistas de música de fondo específicas para ese género.
    *   Usado por el motor para resolver rutas de `musica_fondo`.

### `temp/` (Espacio de Trabajo Temporal)
*   **`input.json`**: El **Puente**. n8n escribe en este archivo; Python lee de él.
*   **`*.jpg`, `*.mp3`, `*.ass`**: Activos intermedios generados durante el proceso de renderizado. Pueden limpiarse seguramente después del renderizado.

### `output/` (Entregables Finales)
*   Almacena los videos `.mp4` renderizados finales.

### `tests/` (Verificación)
*   Contiene scripts de prueba (`test_subprocess.py`) y datos simulados (`test_url_input.json`) usados para depuración y verificación de características.

### `setup/`
*   **`ffmpeg.zip`**: Archivo comprimido con los binarios de FFmpeg.
*   **`requirements.txt`**: Lista de dependencias de Python.

---

## 🐳 Infraestructura: `n8n/`

*   **`docker-compose.yml`**: Define los servicios:
    *   **n8n**: La herramienta de automatización de flujo.
    *   **postgres**: El backend de base de datos para n8n.
    *   **Volúmenes**: Mapea `D:/RODO/Proyectos/ShortsYoutube/NeuroShorts_MVP` a `/home/node/neuroshorts` para permitir escritura de archivos.
*   **`.env`**: Variables de configuración (Contraseñas, Zona Horaria) para Docker.
*   **`init-data.sh`**: Script de inicialización para la base de datos PostgreSQL.

---

## 📝 Puntos de Integración

### El "Apresón de Manos" (n8n ➡️ Python)
1.  **n8n** ejecuta un script Node.js usando el nodo `Execute Command`.
2.  Escribe una cadena JSON a `/home/node/neuroshorts/temp/input.json`.
3.  **Python** lee `D:\...\NeuroShorts_MVP\temp\input.json`.
4.  **Python** parsea el JSON. Si encuentra bloques Markdown (```json), los elimina automáticamente.

### El Protocolo "Descarga Inteligente"
*   Si `path_imagen` es una URL (`http...`) -> Python la descarga usando `requests`.
*   Si `path_imagen` está vacío pero existe `descripcion_visual` -> Python llama a `pollinations.ai` para generarla.
