import os
import json

# 設定圖片目錄
image_dir = "綠藻地圖照片"
images = sorted([f for f in os.listdir(image_dir) if f.startswith("map_") and f.endswith(".png")])

# 儲存為 JSON 檔案
with open("images.json", "w") as f:
    json.dump(images, f)
