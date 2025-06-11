from opc_client_VFD.opcua_client import OPCUAConnection
from scipy.spatial.distance import cosine
import numpy as np
import crawler_esp8266_data #import the .py file of the crawler_esp8266_data
# from stable_baselines3 import PPO
import time

def main(now_vol):
    while True:
        # 從 ESP8266 擷取感測資料
        data = crawler_esp8266_data.get_data()

        # 假設 get_data() 回傳 {'temp': float, 'hum': float}
        now_temp = data['temp']
        now_hum = data['hum']
        ida_temp = 25.0  # 目標溫度
        ida_hum = 60.0   # 目標濕度
        uss_run = True   # 開啟 USS 控制

        # 模型輸入 (標準化觀測值)
        obs = np.array([now_temp / 100, now_hum / 100], dtype=np.float32)
        action, _ = model.predict(obs, deterministic=True)

        print(f"[PPO] Obs: {obs}, Action: {action}")

        # 建立 OPC UA 連線實例
        opc_connection = OPCUAConnection(
            Now_Temp=now_temp,
            Ida_Temp=ida_temp,
            Now_Hum=now_hum,
            Ida_Hum=ida_hum,
            USS_Run=uss_run,
            url=url,
            act=float(action)
        )

        # 啟動資料傳輸（內部會自動連線與傳送）
        opc_connection.connection()

        time.sleep(5)  # 每次執行間隔

if __name__ == "__main__":
    main()
