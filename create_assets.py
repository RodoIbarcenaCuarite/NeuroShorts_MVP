from PIL import Image, ImageDraw, ImageFont
import os

# Create dummy images
assets_dir = r"d:\RODO\Proyectos\ShortsYoutube\NeuroShorts_MVP\assets\Creepy"
os.makedirs(assets_dir, exist_ok=True)

def create_dummy_image(filename, color, text):
    img = Image.new('RGB', (1080, 1920), color=color)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    
    d.text((100, 900), text, fill=(255, 255, 255), font=font)
    img.save(os.path.join(assets_dir, filename))
    print(f"Created {filename}")

create_dummy_image("test_bg_1.jpg", (50, 0, 0), "ESCENA 1\nCREEPY")
create_dummy_image("test_bg_2.jpg", (0, 0, 50), "ESCENA 2\nCREEPY")

# Create dummy audio (1 sec of silence or just a valid file header)
# Minimal MP3 header (not playing silence, simply valid file)
dummy_mp3_path = os.path.join(assets_dir, "ambient.mp3")
with open(dummy_mp3_path, "wb") as f:
    # A tiny valid MP3 frame (MPEG 2.5 Layer III)
    f.write(b'\xff\xe3\x18\xc4\x00\x00\x00\x03\x48\x00\x00\x00\x00') 
print(f"Created {dummy_mp3_path}")
