# 🎬 NeuroShorts MVP - Resumen del Proyecto

## 🧠 ¿Qué es esto?
**NeuroShorts** es una tubería de generación de video automatizada diseñada para crear Shorts de YouTube, TikToks y Reels de alta calidad basados en "Nichos" específicos (ej. Creepy, Curiosidades, Historia).

Combina **n8n** (para automatización de flujo y generación de contenido con IA) con un **Motor de Renderizado Python** personalizado (para ensamblaje de video profesional).

## 🚀 Cómo Funciona (El Flujo)

### 1. El Cerebro (n8n e IA)
*   **n8n** corre en un contenedor Docker.
*   Usa IA (Gemini/OpenAI) para generar un guion, descripciones visuales y estilos de "Nicho" específicos basados en un tema.
*   **Salida**: Genera un archivo JSON estructurado que contiene todos los metadatos del video (Guion, Escenas, Prompts).
*   **Transferencia**: Este JSON se guarda directamente en `NeuroShorts_MVP/temp/input.json` a través de un Volumen Docker compartido.

### 2. El Motor (Python)
*   El script `render_engine.py` detecta el archivo de entrada.
*   **Activos Inteligentes**:
    *   **Imágenes**: Verifica si el JSON tiene URLs. Si sí, las descarga. Si NO (o si fallan), usa **Pollinations AI** para generar imágenes al vuelo basadas en las descripciones visuales.
    *   **Audio**: Genera locuciones (TTS) usando Edge-TTS (tecnología de Microsoft Azure).
    *   **Música**: Selecciona la atmósfera de fondo correcta basada en el Nicho.
*   **Ensamblaje**:
    *   Usa **FFmpeg** (el estándar de la industria para video) para unir todo.
    *   Aplica subtítulos automatizados (quemados) con fuentes/colores específicos por nicho.
    *   Mezcla el audio automáticamente.

### 3. El Resultado
*   Un video `.mp4` pulido se guarda en la carpeta `NeuroShorts_MVP/output`.
*   El nombre del archivo se sanitiza y se marca con fecha/hora (ej. `El_Monstruo_Interno_20251226.mp4`).

---

## ✨ Características Clave
*   **Descarga Inteligente**: Maneja tanto URLs directas como Prompts de Texto (auto-generación).
*   **Tolerancia a Fallos**: Si una imagen falla al descargar, el sistema no colapsa; genera un respaldo o placeholder para asegurar que el video se entregue.
*   **Estilizado por Nicho**: El motor sabe que un video "Creepy" necesita una fuente y música diferentes a un video de "Quiz".
*   **Integración Docker**: Intercambio de archivos fluido entre el mundo de IA contenerizado y el mundo multimedia local de Windows.
