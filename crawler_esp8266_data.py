import requests
import csv
import time
import os


def get_data():
    array=[]
    # === 設定 ===
    esp_url = "http://192.168.244.58/data"
    csv_file = "temperature_humidity_log.csv"
    #interval = 2  # 每幾秒抓一次
    #max_count = 100  # 最多抓幾筆

    # === 檢查是否有舊檔，決定起始 index ===
    file_exists = os.path.exists(csv_file)

    if not file_exists:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Index', 'Timestamp', 'Temperature (°C)', 'Humidity (%)'])

    # 讀取已存在筆數（不包含表頭）
    with open(csv_file, 'r') as f:
        row_count = sum(1 for row in f if row.strip())
        current_index = row_count # 包含表頭 → 第 n 行是第 n-1 筆資料，+1是重第1筆開始算不是從0

    # === 開始抓資料 ===
    #success_count = 0

    try:
        response = requests.get(esp_url, timeout=4)
        data = response.json()

        temp = data['temp']
        hum = data['hum']
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # 寫入資料
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([current_index, timestamp, temp, hum])

        print(f"[{current_index}] {timestamp} - Temperature: {temp}°C, Humidity: {hum}%")

        current_index += 1
        #success_count += 1

        #time.sleep(interval)
        #time.sleep(2)
        array.append(temp)
        array.append(hum)
        return array
        

    except Exception as e:
        print(f"[未寫入] 讀取失敗，重試中：{e}")
        return "Error"
        #time.sleep(2)  # 稍等再重試
