# Mapa de Documentación y Guía de Personalización

Este documento explica **para qué sirve cada archivo** en esta carpeta y **cómo puedes modificar el sistema** (estilos, música, etc.).

---

## 📂 Explicación de Archivos

| Archivo | Función | ¿Cuándo editarlo? |
| :--- | :--- | :--- |
| **`MANUAL_USUARIO_v1_001.md`** | Tu guía principal de "Cómo Usar" el sistema. | Nunca (es lectura). |
| **`GEMINI_SYSTEM_CONTEXT.md`** | **EL CEREBRO**. Contiene el Prompt Maestro que le dice a la IA qué temas usar y cómo escribir. | **SIEMPRE**. Aquí cambias los temas, el estilo de guion y la cantidad de videos. |
| **`N8N_WORKFLOW_SPEC.md`** | Plano técnico del flujo de n8n. | Solo si cambias la lógica interna de n8n (nodos). |
| **`PROJECT_OVERVIEW_ES.md`** | Visión general del proyecto y sus objetivos. | Para leer de qué va el proyecto. |
| **`TECHNICAL_REFERENCE_ES.md`** | Detalles técnicos para programadores (Python, rutas, librerías). | Si vas a tocar el código Python. |


---

## 🎨 Guía de Personalización

### 1. ¿Cómo cambio el Estilo de las Imágenes? (Más amigables / Terror / Realistas)
El sistema usa dos fuentes para decidir cómo se ven las imágenes:
1.  **El Nicho (n8n)**: Si pones "Nicho: Creepy", la IA tiende a pedir oscuridad.
2.  **El Prompt de Gemini (`GEMINI_SYSTEM_CONTEXT.md`)**: Aquí es donde tienes el control total.

**Pasos para cambiar a "Estilo Familiar/Infantil":**
1.  Abre `docs/GEMINI_SYSTEM_CONTEXT.md`.
2.  Busca la sección **Capabilities** o **Visuals**.
3.  Agrega una regla de estilo visual. Por ejemplo:
    ```markdown
    **VISUAL STYLE RULES**:
    - All image descriptions must be bright, colorful, and family-friendly.
    - Avoid scary, dark, or disturbing imagery.
    - Use "Cartoon style" or "Pixar style" keywords in visual descriptions.
    ```
4.  Copia todo el contenido del archivo.
5.  Ve a **n8n** -> Nodo Gemini -> Pega el nuevo texto.
6.  ¡Listo! Los próximos videos pedirán imágenes con ese estilo.

### 2. ¿Cómo cambio la Música?
La música se elige automáticamente según el guion, pero puedes forzarla.
1.  Pon tus archivos `.mp3` en la carpeta `NeuroShorts_MVP/assets/`.
2.  En `GEMINI_SYSTEM_CONTEXT.md`, instruye a la IA para que use esos nombres:
    ```markdown
    **Music Rules**:
    - For happy videos, always suggest "musica: happy_upbeat.mp3".
    ```
3.  Actualiza n8n igual que arriba.

### 3. ¿Cómo hago más (o menos) videos por día?
Por defecto en v1.002 son 18 videos/semana.
1.  Edita `GEMINI_SYSTEM_CONTEXT.md`.
2.  Busca la sección **Weekly Production Schedule**.
3.  Cambia la lista a lo que quieras:
    *   *Ejemplo*: "Generate only 5 videos: 1 Monday, 1 Tuesday...", etc.
4.  Actualiza n8n.
