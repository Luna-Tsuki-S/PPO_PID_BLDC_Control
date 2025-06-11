
"""

# !pip install stable-baselines3 gym numpy matplotlib shimmy
# !pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# !pip install --upgrade stable-baselines3 gymnasium
# !pip install scipy matplotlib pandas


"""# Temp / Humid"""

import gym
import numpy as np
import pandas as pd
from gym import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

# 環境（使用 CSV）
class THBLDC(gym.Env):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.max_steps = len(self.data)

        # 狀態空間：2 維連續數值（標準化）
        self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)

        # 動作空間：0 to 1650 rpm
        self.action_space = spaces.Discrete(1651)
        self.current_step = 0

    def reset(self):
        self.current_step = 0
        return self._get_obs()

    def _get_obs(self):
        row = self.data.iloc[self.current_step]
        return np.array([
            row['Temperature'] / 100,
            row['Humidity'] / 100
        ], dtype=np.float32)

    def step(self, action):
        row = self.data.iloc[self.current_step]
        done = False
        reward = 0



        temp = row['Temperature']
        humid = row['Humidity']

        # RPM rawl
        kwh = ((1650 * (action / 1650) ** 3) * 0.1) / 1000
        tr_fan = 0.006
        save_rate = (kwh - tr_fan) / tr_fan


        # 節能效果（希望 kWh 越少越好）
        reward -= kwh  # 直接懲罰功耗

        # 溫度舒適度（22–28°C 為舒適範圍）
        reward -= abs(temp - 25) * 0.1  # 越接近 25°C 越好

        # 濕度舒適度（40–60% 為舒適範圍）
        reward -= abs(humid - 50) * 0.05  # 越接近 50% 越好

        # 若功耗比基準省電 30% 以上，額外加分
        if save_rate >= 0.3:
            reward += 0.5

        # 若風速在舒適風速區間（ex. 500~900 RPM），額外加分
        if 500 <= action <= 900:
            reward += 0.2

        # 安全風速 <= 1300 RPM
        if action <= 1300:
            reward += 0.2

        self.current_step += 1
        if self.current_step >= self.max_steps - 1:
            done = True

        return self._get_obs(), reward, done, {}

    def render(self, mode='human'):
        row = self.data.iloc[self.current_step]
        print(f"Step {self.current_step} - Temp: {row['temp']}°C, Humid: {row['humid']}%")

# === 訓練模型 ===
csv_path = "/content/temperature_humidity_log.csv"
# csv_path = "/content/sample_data/temperature_humidity_2000.csv"  # 替換為你的 CSV 檔路徑
env = DummyVecEnv([lambda: THBLDC(csv_path)])
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=50000)

# === 儲存模型 ===
model.save("ppo_model")
print("✅ 模型已儲存為 ppo_model.zip")

def test_model(model, env, episodes=500):
    total_rewards = []
    for ep in range(episodes):
        obs = env.reset()
        done = False
        ep_reward = 0
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, _ = env.step(action)
            ep_reward += abs(reward)
        total_rewards.append(ep_reward)
        print(f"Episode {ep+1}: Score = {abs(ep_reward)}")
    print(f"\n📊 Average Score: {np.mean(total_rewards)}")

# === 測試模型執行 ===
test_model(model, env)

# 讀取模型
model = PPO.load("ppo_model.zip")

# 單筆資料（範例）
#  Temperature, Humidity
current_status = [26, 40]


obs = np.array([
    current_status[0] / 100,
    current_status[1] / 100
], dtype=np.float32)



  # 模型預測
action, _ = model.predict(obs, deterministic=True)


print(obs, action)