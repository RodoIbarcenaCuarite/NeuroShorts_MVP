import subprocess
import os

FFMPEG_BIN = r"C:\Users\rodob\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
FFPROBE_BIN = r"C:\Users\rodob\AppData\Local\Microsoft\WinGet\Links\ffprobe.exe"

print("--- Testing FFMPEG ---")
try:
    subprocess.run([FFMPEG_BIN, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✅ FFmpeg success")
except Exception as e:
    print(f"❌ FFmpeg failed: {e}")

print("\n--- Testing FFPROBE ---")
try:
    subprocess.run([FFPROBE_BIN, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✅ FFprobe success")
except Exception as e:
    print(f"❌ FFprobe failed: {e}")
