# Manual de Usuario - NeuroShorts v1.001 (Estable)

## ¿Qué hace este proyecto?
**NeuroShorts** es una "Fábrica Automática de Videos" para YouTube Shorts.
En esta versión **v1.001**, el sistema está configurado en **Modo de Prueba de Estabilidad**.

### Funcionalidad Actual (v1.001):
1.  **Conecta con un "Cerebro" (n8n + Gemini)**: Le pide una idea para un video.
2.  **Genera un Guion**: Crea un script de exactamente **30 segundos** sobre un tema de prueba ("The Bloop").
3.  **Descarga Recursos**: Busca o genera imágenes con IA (Pollinations) de forma segura y paciente (espera 10s para evitar bloqueos).
4.  **Fabrica el Video**: Junta las imágenes, les pone música de fondo, narra el texto (Voz IA) y genera un archivo `.mp4`.

---

## ¿Cómo se usa? (Paso a Paso)

### Prerrequisitos
*   Tener **n8n** corriendo (`docker compose up -d` o tu instalación local).
*   Tener **Python** instalado.

### Ejecución
Solo necesitas abrir tu terminal en la carpeta del proyecto y correr **un comando**:

```bash
python master_weekly.py
```

### ¿Qué verás pasar?
1.  La terminal dirá `🏭 INICIANDO NEUROSHORTS FACTORY 🏭`.
2.  Verás `📡 [n8n] Solicitando guiones...`.
3.  Luego `✨ [Proyecto] Nuevo: 01_Test_Creepy_El Misterio de The Bloop`.
4.  Empezará a descargar imágenes (`⬇️ Descargando Escena 1...`). **Ten paciencia**, espera 10 segundos entre cada una.
5.  Finalmente dirá `✅ Video created` y te mostrará la ruta del video final.

### ¿Dónde está mi video?
Tu video listo para subir estará en:
`NeuroShorts_MVP/PRODUCCION/Salida_Semanal/`

---

## Solución de Problemas Comunes

| Problema | Solución |
| :--- | :--- |
| **"Read timed out"** | n8n tardó mucho. El sistema ahora espera hasta 5 min. Solo reintenta. |
| **"Invalid JSON"** | El "Cerebro" respondió texto en vez de código. La v1.001 ya tiene un filtro para arreglar esto automáticamente. |
| **Imágenes Pixeladas** | Es por pedir muchas muy rápido. La v1.001 espera 10s entre imágenes para evitarlo. |
