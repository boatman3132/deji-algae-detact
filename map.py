import os
import time
import pandas as pd
import folium
import branca.colormap as cm
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 設定 Selenium Chrome driver 選項
chrome_options = Options()
chrome_options.add_argument("--headless")  # 無頭模式
chrome_options.add_argument("--window-size=1280,800")  # 設定視窗大小

# ✅ 使用 webdriver-manager 自動下載並匹配 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)





# 讀取 CSV 檔案
csv_file = "測試.csv"  # 請確保 CSV 檔案在同一目錄下
df = pd.read_csv(csv_file)

# 確保 algae 欄位是數字
df["algae"] = pd.to_numeric(df["algae"], errors="coerce")
df.dropna(subset=["algae"], inplace=True)
df["algae"] = df["algae"].astype(float)

# 確保 time 欄位是時間格式
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df.dropna(subset=["time"], inplace=True)

# 按月份分類
df["year_month"] = df["time"].dt.to_period("M")

# 設定顏色範圍（讓顏色變化更明顯）
vmin = 0
vmax = 250  # 設定最大值範圍
if vmin == vmax:
    vmax += 1

# 增加顏色對比（淺綠 深綠→ 黃 → 橘 → 紅 → 深紅）
color_scale = cm.LinearColormap(
    colors = ["#a8f08e", "#00a000", "#ffd700", "#ff9800", "#ff4500", "#8b0000"],
    vmin=vmin,
    vmax=vmax,
)

# 顏色函數
def get_color(value):
    return color_scale(value)

# 確保輸出資料夾存在 (maps 資料夾)
output_folder = "maps"
os.makedirs(output_folder, exist_ok=True)

# 依時間區間生成多個地圖 HTML 檔案
map_files = []
for period, group in df.groupby("year_month"):
    m = folium.Map(location=[24.2565, 121.1966], zoom_start=14, tiles="CartoDB Positron", attr="CartoDB")

    # 加入站點標記
    for _, row in group.iterrows():
        # 建立圓形標記
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=17,  # 點的半徑
            color=None,
            fill=True,
            fill_color=get_color(row["algae"]),
            fill_opacity=1.0,
            popup=folium.Popup(
                f"<div style='width:250px;'>"
                f"<b>站點名稱：</b> {row['station']}<br>"
                f"<b>藻類數量：</b> {row['algae']}<br>"
                f"<b>時間：</b> {row['time'].strftime('%Y-%m-%d')}"
                f"</div>",
                max_width=300,
            ),
        ).add_to(m)

        # 利用 DivIcon 在相同座標顯示藻類數值，並設定文字置中與白色外框
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.DivIcon(
                icon_size=(30, 30),          # 設定圖示大小
                icon_anchor=(15, 15),        # 將圖示錨點置中
                html=f"""<div style="
                            font-size: 18px; 
                            font-weight: bold;
                            color: black;
                            text-align: center;
                            line-height: 30px;
                            background-color: transparent;">
                        {int(row["algae"])}
                        </div>""",
            ),
        ).add_to(m)


    # 加入顏色圖例
    color_scale.caption = "藻類數量分佈"
    m.add_child(color_scale)

    # 儲存地圖 HTML
    file_name = f"{output_folder}/map_{period}.html"
    m.save(file_name)
    map_files.append(file_name)

print("✅ 地圖已成功生成，儲存於 maps 資料夾！")

# 使用 Selenium 進行截圖並裁切 (從 (20,0) 到 (width, height-20))
# 確保 screenshots 資料夾存在
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)


for html_file in map_files:
    # 取得 HTML 檔案的絕對路徑，並以 file 協議開啟
    file_path = os.path.abspath(html_file)
    file_url = "file://" + file_path
    driver.get(file_url)
    time.sleep(2)  # 等待地圖載入

    # 截取螢幕畫面，暫存為圖片
    temp_screenshot = "temp_screenshot.png"
    driver.save_screenshot(temp_screenshot)

    # 使用 PIL 裁切圖片 (從 (20,0) 到 (width, height-20))
    image = Image.open(temp_screenshot)
    width, height = image.size
    cropped = image.crop((100, 0, width, height - 20))

    # 儲存裁切後的圖片，檔名與 HTML 檔案相對應
    base_name = os.path.basename(html_file).replace(".html", ".png")
    cropped.save(os.path.join(screenshot_folder, base_name))

# 清理暫存檔案與關閉瀏覽器 driver
driver.quit()
if os.path.exists(temp_screenshot):
    os.remove(temp_screenshot)

print("✅ 截圖已成功生成，儲存於 screenshots 資料夾！")
 