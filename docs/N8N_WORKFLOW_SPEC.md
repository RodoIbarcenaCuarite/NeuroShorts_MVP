# 📡 Guía de Configuración n8n - NeuroShorts Factory

Para que `ideation.py` funcione, debes crear un **Workflow en n8n** con 3 pasos clave.

## 1. El Catalizador (Webhook Trigger)
*   **Nodo**: `Webhook`
*   **Método**: `POST`
*   **Path**: `generador-semanal` (o el que tú elijas).
*   **Authentication**: None (para pruebas locales) o Header Auth.
*   **Respuesta**: "Using 'Respond to Webhook' Node".
*   **URL Final**: Copia la "Test URL" o "Production URL" (ej: `https://tuhook.n8n.cloud/webhook/generador-semanal`).
*   👉 **ACCIÓN**: Pega esta URL en el archivo `.env` de NeuroShorts.

## 2. El Cerebro (Gemini / LLM Chain)
*   **Entrada**: Recibe `{"fecha": "2024-..."}` del Webhook.
*   **Nodo Generativo**: Conecta n8n con **Google Gemini Chat**.
*   **Prompt del Sistema**: Copia y pega el contenido de `docs/GEMINI_SYSTEM_CONTEXT.md`.
*   **Prompt del Usuario**: "Genera 6 guiones de Shorts para la semana que inicia en {fecha}."

## 3. La Entrega (Respond to Webhook)
*   **Nodo**: `Respond to Webhook`
*   **Format**: `JSON`
*   **Response Body**: Debe ser el **Output del LLM**.
*   **IMPORTANTE**: El JSON debe ser una **Lista de Objetos** directa (Array), así:

```json
[
  {
    "dia": "01_Lunes",
    "nicho": "History",
    "titulo": "Plaga_Baile",
    "guion": { ... }
  },
  {
    "dia": "02_Martes",
    ...
  }
]
```

---
### 🛠️ Troubleshooting (Si falla)
Si `ideation.py` da error, casi siempre es porque el LLM devolvió texto extra (ej. "Aquí tienes tu JSON: ...").
*   Asegúrate de usar un nodo **"Code"** o **"Output Parser"** en n8n entre el LLM y el Webhook final para limpiar el texto y dejar solo el JSON puro.
