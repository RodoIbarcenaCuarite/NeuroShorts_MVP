import time
import sys
import subprocess
from pathlib import Path
import os

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent # NeuroShorts_MVP/
TEMP_DIR = BASE_DIR / "temp"
INPUT_FILE = TEMP_DIR / "input.json"
RENDER_SCRIPT = BASE_DIR / "src" / "render_engine.py"

print(f"👀 NeuroShorts Watcher Active")
print(f"📂 Monitoring: {INPUT_FILE}")
print("---------------------------------------------------")

last_mtime = 0

def get_file_mtime(path):
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return 0

# Initial check
if INPUT_FILE.exists():
    last_mtime = get_file_mtime(INPUT_FILE)

while True:
    try:
        time.sleep(1) # Check every 1 second
        
        # print(".", end="", flush=True) # Heartbeat
        
        if not INPUT_FILE.exists():
            continue
            
        current_mtime = get_file_mtime(INPUT_FILE)
        
        # Check if file is modified
        if current_mtime != last_mtime:
            print(f"\n🔍 Change detected! (Old: {last_mtime} -> New: {current_mtime})")
            # Wait a bit to ensure n8n finished writing
            time.sleep(1) 
            
            # Double check modification to avoid rapid firing
            if get_file_mtime(INPUT_FILE) == current_mtime:
                print(f"\n⚡ New Input Detected! ({time.strftime('%H:%M:%S')})")
                print("🎬 Triggering Render Engine...")
                
                try:
                    subprocess.run(
                        [sys.executable, str(RENDER_SCRIPT), str(INPUT_FILE)],
                        check=True
                    )
                    print("✅ Render Cycle Complete. Waiting for next input...")
                except subprocess.CalledProcessError:
                    print("❌ Render Failed. Retrying on next change.")
                except Exception as e:
                    print(f"❌ Error launching script: {e}")
                
                last_mtime = current_mtime
                print("👀 Watching...")
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping Watcher.")
        break
    except Exception as e:
        print(f"❌ Loop Error: {e}")
        time.sleep(5)
