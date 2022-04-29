# 상장하면 떡상하는지 알아보는 코드
# %%
import json
import pickle
import requests
import pyupbit

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute1", count=1000)

# %%
print(df)

# %%

url = "https://api.upbit.com/v1/market/all"

querystring = {"isDetails": "false"}

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)


# %%


# li = pickle.loads(response.text)
# # %%
# li
# %%
print(response.text)
# %%
_dict = json.loads(response.text)

# %%

for d in _dict:
    if d["market"] == "KRW-AXS":
        print(d)
# print(_dict)
# https://docs.upbit.com/reference#
# 마켓코드 조회
# json 역직렬화
# 새로운거 나오면 비교
# %%

url = "https://api.upbit.com/v1/candles/days"

querystring = {"market": "BTC-GRT", "count": "10000000"}

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

for data in json.loads(response.text):
    print(data["trade_price"])
# print(response.text)
# %%

# 결론
# 상장하면 가격 떨어짐
