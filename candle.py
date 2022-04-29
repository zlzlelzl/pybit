# %%
import pyupbit
import mpl_finance
# import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import requests

# api_key = ""
# api_secret = ""
# api_key = ""  # test
# api_secret = ""  # test
base_url = "https://www.bitmex.com/api/v1"

path = "/trade/bucketed"  # "/history"
headers = {"Accept": "application/json"}
data = {
    "api-key": api_key,
    "symbol": "XBTUSD",
    "count": "30",
    "reverse": "true"
}
data["binSize"] = "1m"


raw_data = requests.get(base_url + path, headers=headers, data=data).json()

if raw_data[0]["timestamp"] > raw_data[1]["timestamp"]:
    data = pd.DataFrame(raw_data)[::-1]
else:
    data = pd.DataFrame(raw_data)


# def get_price_data_from_upbit():
#     interval = "minute15"  # minute1
#     count = 100  # 100000000
#     df = pyupbit.get_ohlcv("KRW-BTC", interval=interval, count=count)

#     df.to_csv(f"data_{interval}_count_{count}.csv")

#     data = pd.read_csv(f"data_{interval}_count_{count}.csv")


# def get_price_data_from_bitmex(day):  # '2022-02-04 16:10:00'

#     def str_to_timestamp(s):
#         return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())

#     end = int(time.time())
#     start = int(str_to_timestamp(day))

#     url = f"https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=1&from={start}&to={end}"
#     res = requests.get(url).json()


# get_price_data_from_bitmex(day)

# %%
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)

if "Unnamed: 0" in data.columns:  # 업비트
    data = data.rename(columns={"Unnamed: 0": "date"})
elif "timestamp" in data.columns:  # 비트멕스
    data = data.rename(columns={"timestamp": "date"})

avg20 = []
ubb = []
lbb = []
for i in range(20):
    avg20.append(data["close"][i])
    ubb.append(data["close"][i])
    lbb.append(data["close"][i])


bought_upper_ubb = []
bought_upper_date = []
sold_upper_ubb = []
sold_upper_date = []
bought_lower_ubb = []
bought_lower_date = []
sold_lower_ubb = []
sold_lower_date = []

is_bought_upper_ubb = False
is_bought_lower_lbb = False
is_bought_regression_ubb = False
is_bought_regression_lbb = False

for i in range(20, len(data["date"])):
    avg20.append(np.mean(data["close"][i-20:i]))
    ubb.append(np.mean(data["close"][i-20:i]) +
               2 * np.std(data["close"][i-20:i]))
    lbb.append(np.mean(data["close"][i-20:i]) -
               2 * np.std(data["close"][i-20:i]))

    # 볼린저 밴드 탈출 추격매수
    if not is_bought_upper_ubb and data["high"][i] > ubb[i]:
        bought_upper_ubb.append(ubb[i])
        bought_upper_date.append(data["date"][i])
        is_bought_upper_ubb = True

    # 음전할때 팖
    if is_bought_upper_ubb and (data["close"][i] < data["open"][i] or data["close"][i] < ubb[i]):
        sold_upper_ubb.append(data["close"][i])
        sold_upper_date.append(data["date"][i])
        is_bought_upper_ubb = False

    if not is_bought_lower_lbb and data["low"][i] < lbb[i]:
        bought_lower_ubb.append(ubb[i])
        bought_lower_date.append(data["date"][i])
        is_bought_lower_lbb = True

    # 양전할때 팖
    if is_bought_lower_lbb and (data["close"][i] > data["open"][i] or data["close"][i] > lbb[i]):
        sold_lower_ubb.append(data["close"][i])
        sold_lower_date.append(data["date"][i])
        is_bought_lower_lbb = False
    # 볼린저 밴드 탈출 추격매수 끝

    # 볼린저 밴드 회귀 매수
    # if data["open"][i]


data["avg20"] = avg20
data["ubb"] = ubb
data["lbb"] = lbb

plt.plot(data["date"], data["avg20"], color="orange")
plt.plot(data["date"], data["ubb"], color="red")
plt.plot(data["date"], data["lbb"], color="blue")

mpl_finance.candlestick2_ohlc(ax, opens=data['open'], highs=data['high'],
                              lows=data['low'], closes=data['close'], width=0.5, colorup='r', colordown='b')

plt.show()
# %%
# 안 팔고 들고있는거는 계산x
bought_upper_ubb = bought_upper_ubb[:len(sold_upper_ubb)]
bought_lower_ubb = bought_lower_ubb[:len(sold_lower_ubb)]
# %%
# 롱 포지션
# np.array(sold_upper_ubb) - np.array(bought_upper_ubb)
# %%
# 숏 포지션
# np.array(bought_lower_ubb) - np.array(sold_lower_ubb)
# %%
# (1비트, x1 레버리지 투자시)
# 롱 총 수익
sum(sold_upper_ubb) - sum(bought_upper_ubb)
# %%
# 숏 총 수익
sum(bought_lower_ubb) - sum(sold_lower_ubb)
# %%
# 롱 승률
profit_day = 0
for i in range(len(sold_upper_ubb)):
    if sold_upper_ubb[i] - bought_upper_ubb[i] >= 0:
        profit_day += 1

print(profit_day / len(sold_upper_ubb) * 100)
# %%
# 숏 승률
profit_day = 0
for i in range(len(bought_lower_ubb)):
    if bought_lower_ubb[i] - sold_lower_ubb[i] >= 0:
        profit_day += 1

print(profit_day / len(sold_lower_ubb) * 100)

# %%

# %%
