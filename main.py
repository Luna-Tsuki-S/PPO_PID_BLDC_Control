from opc_client_VFD import connection
from scipy.spatial.distance import cosine
import numpy as np
import crawler_esp8266_data #import the .py file of the crawler_esp8266_data
from stable_baselines3 import PPO
import time

def main(now_vol):
    while True:
        url = "opc.tcp://192.168.0.1:4840"

        #get esp8266 return temperature
        data = crawler_esp8266_data.get_data()
        Ida_Temp = 25
        Now_Temp =  data['temp']
        hum = data['hum']
        USS_Run = 1

        #decision from PPO
        model = PPO.load("ppo_model.zip")

       
        obs = np.array([
            data[0] / 100,
            data[1] / 100
        ], dtype=np.float32)



        # 模型預測
        action, _ = model.predict(obs, deterministic=True)


        print(obs, action)


        # Create instance of OPC_UA_CONNECTION
        opc_connection = connection(Ida_Temp, Now_Temp, USS_Run, url, act = action)

        # Start the connection
        if not opc_connection.connection():
            print("Connection completed")

        time.sleep(2)

main(
