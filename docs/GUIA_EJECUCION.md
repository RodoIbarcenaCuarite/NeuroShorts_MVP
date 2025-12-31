# 🎮 Guía de Ejecución: NeuroShorts MVP

Este documento explica cómo operar el sistema, tanto en modo automático (producción) como en modo manual (pruebas).

## 🤖 Método 1: Piloto Automático (n8n + Auto-Pilot)
Este es el modo normal de producción.

1.  **Ejecuta `auto_pilot.bat`** en tu Windows (Doble Click).
    *   Se abrirá una ventana negra que dice "👀 NeuroShorts Watcher Active". Déjala abierta.
2.  **Entra a n8n** y ejecuta tu flujo.
3.  **¿Qué pasa después?**
    *   n8n genera el `input.json` en la carpeta compartida.
    *   ¡El `auto_pilot.bat` detecta el cambio instantáneamente y crea el video!
    *   El video final aparece en `output/`.

### ⚠️ Requisito Crucial en n8n
Para que esto funcione, tu flujo de n8n DEBE tener un último nodo que guarde el archivo.
*   **Nodo:** "Execute Command".
*   **Comando:** `printf '%s' '{{JSON.stringify($json)}}' > /home/node/neuroshorts/temp/input.json`
*   **Nota:** Usamos `printf` porque `echo` puede romper el JSON si hay símbolos extraños.

*Nota: No necesitas configurar "Execute Command" para correr Python, porque tu Windows está vigilando.*

---

## 🕹️ Método 2: Control Manual (¡A Voluntad!)
Útil si quieres volver a generar el *mismo* video (por ejemplo, después de arreglar algo en el código) sin gastar tokens de IA ni esperar a n8n.

### Opción A: "Doble Click" (La más fácil)
1.  Ve a la carpeta `NeuroShorts_MVP`.
2.  Busca el archivo **`run_neuroshorts.bat`**.
3.  Hazle **Doble Click**.
    *   *Comportamiento*: Buscará automáticamente el último archivo generado por n8n (`temp/input.json`) y volverá a crear el video.
    
### Opción B: "Arrastrar y Soltar" (Para probar nuevos guiones)
Si has creado un archivo de prueba (ej. `mi_test.json`), simplemente:
1.  Agarra tu archivo JSON con el mouse.
2.  Arrastralo SOBRE el archivo `run_neuroshorts.bat`.
3.  El sistema renderizará ESE video específico.

---

## 🛠️ Cómo crear tus propios tests
Si quieres probar ideas sin usar la IA:

1.  Ve a `NeuroShorts_MVP/tests/`
2.  Copia un archivo existente (ej. `test_url_input.json`) y pégalo en tu escritorio.
3.  Ábrelo con el Bloc de Notas y edita el texto o las URLs de las imágenes.
4.  Usa el **Método 2 Opción B** (Arrastrar y Soltar) para ver tu creación.

---

## ⚠️ Solución de Problemas Comunes

*   **"No se encuentra el módulo..."**: Asegúrate de haber instalado los requisitos (`pip install -r setup/requirements.txt`).
*   **"Video de 0kb"**: Revisa que el título en el JSON no tenga caracteres raros (aunque el sistema ya lo autoprotege).
*   **"Pantalla Negra"**: Significa que la imagen falló al descargar y falló al generar. Revisa tu conexión a internet.
