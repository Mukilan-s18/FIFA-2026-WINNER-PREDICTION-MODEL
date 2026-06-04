from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import os
import random

# Generate a cinematic dark stadium background
def create_background(width=1024, height=1024):
    bg = Image.new("RGBA", (width, height), (10, 15, 25, 255))
    draw = ImageDraw.Draw(bg)
    
    # Add a subtle gradient from top to bottom
    for y in range(height):
        r = int(10 + (20 * (y / height)))
        g = int(15 + (25 * (y / height)))
        b = int(25 + (30 * (y / height)))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Add some "stadium lights" (blurred glowing circles)
    light_layer = Image.new("RGBA", (width, height), (0,0,0,0))
    ldraw = ImageDraw.Draw(light_layer)
    for _ in range(15):
        lx = random.randint(0, width)
        ly = random.randint(0, height // 2)
        r = random.randint(10, 40)
        ldraw.ellipse([lx-r, ly-r, lx+r, ly+r], fill=(255, 255, 230, 80))
    
    light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=15))
    bg.paste(light_layer, (0, 0), light_layer)
    
    return bg

bg = create_background()

players = [
    ("Jude Bellingham", "england"),
    ("Kylian Mbappe", "france")
]

for name, team in players:
    raw_path = name.replace(" ", "_").lower() + "_raw.png"
    if not os.path.exists(raw_path):
        print(f"File {raw_path} not found.")
        continue
    
    player_img = Image.open(raw_path).convert("RGBA")
    
    # Scale player to fit well within 1024x1024
    aspect_ratio = player_img.width / player_img.height
    new_height = 950
    new_width = int(new_height * aspect_ratio)
    player_img = player_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a fresh copy of the background
    final_img = bg.copy()
    
    # Add a slight dark vignette behind the player
    draw = ImageDraw.Draw(final_img)
    draw.rectangle([0, 800, 1024, 1024], fill=(0,0,0,150))
    
    # Calculate position (bottom center)
    x = (1024 - new_width) // 2
    y = 1024 - new_height
    
    # Paste player onto background
    final_img.paste(player_img, (x, y), player_img)
    
    # Apply a slight color grade to make it look cinematic (increase contrast slightly)
    final_img = final_img.convert("RGB")
    enhancer = ImageEnhance.Contrast(final_img)
    final_img = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Color(final_img)
    final_img = enhancer.enhance(1.1)
    
    # Save the generated image directly to the public folder
    output_path = f"public/{team}_spotlight.png"
    final_img.save(output_path, "PNG")
    print(f"Generated {output_path}")
