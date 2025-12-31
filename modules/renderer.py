import os
import json
import subprocess
from pathlib import Path

# Config
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "PRODUCCION" / "Salida_Semanal"

def render_ready_projects(weekly_folder: Path):
    """
    Busca proyectos en estado READY y los manda al render_engine.py original
    pero inyectándole los paths correctos.
    """
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
        
    print(f"🎬 [Render] Buscando proyectos listos en: {weekly_folder.name}")
    
    for project_dir in weekly_folder.iterdir():
        if not project_dir.is_dir(): continue
        
        metadata_path = project_dir / "metadata.json"
        if not metadata_path.exists(): continue
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            
        if metadata.get("status") == "READY":
            print(f"🚀 [Ejecutando] Render para: {project_dir.name}")
            
            # Llamamos al script legacy pero pasándole el guion json de este proyecto
            guion_path = project_dir / "guion.json"
            
            # NOTA: El render_engine original leía de 'temp/'. 
            # Para la Fase 2, necesitaremos adaptar render_engine.py para aceptar 
            # paths de entrada O usar este wrapper para copiar archivos a temp.
            # SOLUCIÓN PRO: Ejecutar render_engine pasándole el JSON absoluto.
            
            cmd = ["python", f"{BASE_DIR}/src/render_engine.py", str(guion_path)]
            
            try:
                subprocess.run(cmd, check=True)
                
                # Mover el video generado a Salida_Semanal
                # 1. Identificar el video más reciente en output/
                original_output_dir = BASE_DIR / "output"
                list_of_files = list(original_output_dir.glob('*.mp4'))
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    
                    target_file = OUTPUT_DIR / latest_file.name
                    latest_file.rename(target_file)
                    print(f"📦 [Movido] Video guardado en: {target_file}")
                
                # Actualizar estado a DONE
                metadata["status"] = "DONE"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"✅ [Completo] Video generado para: {project_dir.name}")
                
            except subprocess.CalledProcessError:
                print(f"❌ [Error] Falló el render de: {project_dir.name}")
                metadata["status"] = "RENDER_ERROR"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    pass
