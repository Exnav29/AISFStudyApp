from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, filename):
    image = Image.new('RGB', (size, size), color='#4a0e78')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    # Calculate text size using textbbox
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='#FFFFFF', font=font)
    
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    image.save(os.path.join(icons_dir, filename))

create_icon(192, 'A/AISF\n192x192', 'icon-192x192.png')
create_icon(512, 'A/AISF\n512x512', 'icon-512x512.png')

print("Placeholder icons created successfully.")
