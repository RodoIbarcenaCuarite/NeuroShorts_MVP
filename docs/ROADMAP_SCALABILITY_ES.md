# 🗺️ Hoja de Ruta de Escalabilidad: De MVP a Producto Profesional

Esta hoja de ruta describe los pasos necesarios para profesionalizar el proyecto **NeuroShorts**, migrando de una prueba de concepto local a un sistema robusto, escalable y mantenible.

## 🟢 Fase 1: Profesionalización del Código (Inmediato)
*   **Control de Versiones (Git)**:
    *   Iniciar repositorio Git.
    *   Crear `.gitignore` estricto (ignorar `temp/`, `output/`, `venv/`, `.env`).
    *   Usar ramas (`main` para estable, `dev` para desarrollo).
*   **Modularización de Python**:
    *   Romper el monolito `render_engine.py`.
    *   Crear estructura de paquete:
        ```
        src/
        ├── engines/
        │   ├── audio.py
        │   ├── visuals.py
        │   └── subtitle.py
        ├── models/
        │   └── data_schema.py
        └── main.py
        ```
*   **Manejo de Errores y Logging**:
    *   Reemplazar `print()` con un logger real (`logging` module).
    *   Guardar logs en archivos rotativos (`logs/app.log`) para autopsias de errores.

## 🟡 Fase 2: Gestión de Activos y Nube (Corto Plazo)
*   **Almacenamiento de Assets en la Nube**:
    *   Mover `assets/` (música, fuentes) a AWS S3 o Google Cloud Storage.
    *   El motor descargará assets bajo demanda (caché local) en lugar de depender de carpetas locales.
*   **Salida a la Nube**:
    *   Subir el video final renderizado (`output/`) automáticamente a una carpeta de Google Drive o un Bucket S3, generando un link compartible.

## 🟠 Fase 3: Desacoplamiento e Infraestructura (Mediano Plazo)
*   **Cola de Mensajes (Redis/RabbitMQ)**:
    *   Reemplazar el sistema de "ver archivo `input.json`" por una cola real.
    *   n8n envía mensaje a RabbitMQ -> Worker de Python consume y procesa. Esto permite tener múltiples renders simultáneos.
*   **API REST (FastAPI)**:
    *   Envolver el motor en una API.
    *   n8n hace POST a `localhost:8000/render` en lugar de usar comandos de consola.
    *   Permite monitoreo de estado en tiempo real.

## 🔴 Fase 4: Producción y CI/CD (Largo Plazo)
*   **CI/CD Pipelines (GitHub Actions)**:
    *   Correr tests automáticos (`pytest`) antes de cada merge.
    *   Linting de código (Black/Flake8) para calidad.
*   **Contenerización Total**:
    *   Crear un `Dockerfile` para el motor de Python.
    *   Orquestar todo (n8n + Postgres + Python Worker) en un solo `docker-compose` o Kubernetes.

---

## ✅ Resumen de Próximos Pasos (Accionables)
1.  [ ] `git init` y subir a GitHub/GitLab.
2.  [ ] Separar lógica de `render_engine.py` en módulos.
3.  [ ] Configurar un sistema de logs real.
