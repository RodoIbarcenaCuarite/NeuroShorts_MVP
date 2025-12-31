import argparse
import datetime
from pathlib import Path
from modules import ideation, asset_manager, renderer

# Directorio base
BASE_DIR = Path(__file__).resolve().parent
PRODUCCION_DIR = BASE_DIR / "PRODUCCION"

def get_current_week_folder():
    dt = datetime.date.today()
    return PRODUCCION_DIR / f"{dt.year}_Semana_{dt.isocalendar()[1]}"

def main():
    parser = argparse.ArgumentParser(description="NeuroShorts Factory Master Control")
    parser.add_argument("--mode", choices=["all", "ideation", "assets", "render"], default="all")
    parser.add_argument("--date", help="Fecha base (YYYY-MM-DD)", default=None)
    
    args = parser.parse_args()
    
    print("🏭 INICIANDO NEUROSHORTS FACTORY 🏭")
    
    # 1. Ideación (Lunes)
    if args.mode in ["all", "ideation"]:
        success = ideation.generar_semana(args.date)
        if not success:
            print("🛑 [CRITICAL] Deteniendo fábrica por error en Ideación (n8n no respondió o falló).")
            return
        
    # Identificar carpeta de la semana
    week_folder = get_current_week_folder()
    if not week_folder.exists():
        print(f"❌ No se encontró la carpeta de la semana: {week_folder}")
        return

    # 2. Gestión de Assets (Martes/Continuo)
    if args.mode in ["all", "assets"]:
        asset_manager.check_and_download_assets(week_folder)

    # 3. Renderizado (Jueves/Final)
    if args.mode in ["all", "render"]:
        renderer.render_ready_projects(week_folder)
        
    print("🏁 [Factory] Ciclo finalizado.")

if __name__ == "__main__":
    main()
