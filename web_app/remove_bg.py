import sys
from PIL import Image

def remove_black_bg(input_path, output_path, threshold=10):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Check if the pixel is dark enough
        if item[0] < threshold and item[1] < threshold and item[2] < threshold:
            newData.append((255, 255, 255, 0)) # Transparent
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")

remove_black_bg("/Users/mukilan/.gemini/antigravity-ide/brain/bbe970c0-692b-45b7-994b-256444488201/media__1780548290513.jpg", "/Users/mukilan/FIFA 2026 WINNER PREDICTION MODEL/web_app/public/spain_custom_cutout.png")
print("Done")
