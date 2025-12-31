import os
import json
import requests
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuración
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
PRODUCCION_DIR = BASE_DIR / "PRODUCCION"

def generar_semana(fecha_inicio: str = None):
    """
    1. Llama a n8n para obtener 6 ideas.
    2. Crea la estructura de carpetas para la semana.
    3. Guarda los guiones.
    """
    if not fecha_inicio:
        fecha_inicio = datetime.date.today().isoformat()
    
    # Calcular semana
    dt = datetime.datetime.fromisoformat(fecha_inicio)
    nombre_semana = f"{dt.year}_Semana_{dt.isocalendar()[1]}"
    semana_path = PRODUCCION_DIR / nombre_semana
    
    print(f"🧠 [Ideación] Iniciando generación para: {nombre_semana}")
    
    if not N8N_WEBHOOK_URL or "reemplazar-aqui" in N8N_WEBHOOK_URL:
        print("⚠️ [Advertencia] N8N_WEBHOOK_URL no configurado en .env.")
        print("   Por favor edita: NeuroShorts_MVP/.env")
        return False
        
    print(f"📡 [n8n] Solicitando guiones al Cerebro... (Esto puede tardar unos segundos)")
    try:
        # Aumentamos timeout a 300s (5 min) por si n8n tarda generando ideas
        response = requests.post(N8N_WEBHOOK_URL, json={"fecha": fecha_inicio}, timeout=300)
        response.raise_for_status()
        data = response.json()
        
        print(f"🕵️ [Debug] JSON recibido de n8n ({type(data)}): {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...") # Debug info

        # Validación básica
        if not isinstance(data, list):
             # Si n8n devuelve un wrapper {data: [...]}, intentamos extraerlo
             if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                 data = data["data"]
             else:
                 print(f"❌ Error: n8n respondió con formato inválido (Esperaba lista).")
                 print(f"Recibido: {json.dumps(data)[:200]}")
                 return False
                 
    except Exception as e:
        print(f"❌ Error conectando con n8n: {e}")
        return False

    # Crear carpetas
    if not semana_path.exists():
        semana_path.mkdir(parents=True)
        print(f"📁 [Carpeta] Creada: {semana_path}")

    for item in data:
        # Normalización de claves (Robustez ante n8n/LLM)
        dia = item.get('dia') or item.get('day') or item.get('Day')
        nicho = item.get('nicho') or item.get('niche') or item.get('Niche')
        titulo = item.get('titulo') or item.get('title') or item.get('Title')
        
        if not dia or not nicho or not titulo:
            print(f"⚠️ [Skipping] Item incompleto: {item}")
            continue

        folder_name = f"{dia}_{nicho}_{titulo}"
        project_path = semana_path / folder_name
        
        # Determinar el objeto guion (Puede estar anidado o ser el item mismo)
        guion_data = item.get('guion', item)

        if not project_path.exists():
            project_path.mkdir()
            print(f"✨ [Proyecto] Nuevo: {folder_name}")
            
            # Guardar Guion (Solo si es nuevo)
            with open(project_path / "guion.json", "w", encoding="utf-8") as f:
                json.dump(guion_data, f, indent=2, ensure_ascii=False)
            
            # Inicializar Metadata
            metadata = {
                "status": "CREATED", 
                "created_at": datetime.datetime.now().isoformat(),
                "intentos_assets": 0
            }
            with open(project_path / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        else:
            print(f"🛡️ [Persistencia] Saltando script existente: {folder_name}")
            # No tocamos ni guion ni metadata. El Asset Manager se encargará de repararlo si hace falta.
            
    return True

if __name__ == "__main__":
    generar_semana()
