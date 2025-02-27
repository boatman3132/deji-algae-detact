import pandas as pd
import matplotlib.pyplot as plt

# 讀取 CSV 檔案
file_path = "總藻.csv"  # 確保 CSV 檔案與此腳本放在相同目錄
df = pd.read_csv(file_path)

# 轉換日期格式
df['總藻'] = pd.to_datetime(df['總藻'], format="%Y/%m")

# 按日期排序
df = df.sort_values(by='總藻')

# 創建圖表
fig, ax = plt.subplots(figsize=(10, 1))

# 繪製折線（移除點）
ax.plot(df['總藻'], df['平均'], linestyle='-', linewidth=2)

# 移除所有視覺元素（軸線、標籤、格線等）
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.set_frame_on(False)

# 儲存圖片（透明背景）
output_path = "algae_trend.png"
plt.savefig(output_path, bbox_inches='tight', transparent=True)

print(f"折線圖已儲存至 {output_path}")
