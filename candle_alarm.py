# %%
from api_key import *
import ccxt
from pyTelegram import send_message
# import mpl_finance
# import pandas_datareader.data as web
# import datetime
# import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np
import time
import requests

# api_key = ""
# api_secret = ""
# api_key = ""  # test
# api_secret = ""  # test

base_url = "https://www.bitmex.com/api/v1"
# base_url = "https://testnet.bitmex.com/api/v1"

# curl -X GET --header 'Accept: application/json' 'https://www.bitmex.com/api/v1/quote?&count=100&'

path = "/trade/bucketed"  # "/history"
# headers = {"Accept": "application/json"}
# data = {
#     "symbol": "XBTUSD",
#     "count": "1000",
#     "reverse": "true"
# }
# data["binSizes[binSize_i]"] = "1m"


# raw_data = requests.get(base_url + path, headers=headers, data=data).json()

# if raw_data[0]["timestamp"] > raw_data[1]["timestamp"]:
#     data = pd.DataFrame(raw_data)[::-1]
# else:
#     data = pd.DataFrame(raw_data)

bought_upper_ubb = []
bought_upper_date = []
sold_upper_ubb = []
sold_upper_date = []
bought_lower_ubb = []
bought_lower_date = []
sold_lower_ubb = []
sold_lower_date = []

binSizes = ["1m"]
# , "5m", "1h", "1d"]

is_bought_upper_ubb = [False] * len(binSizes)
is_bought_lower_lbb = [False] * len(binSizes)
is_bought_ubb_cross = False
is_bought_lbb_cross = False

bit = ccxt.bitmex({
    'apiKey': api_key,
    'secret': api_secret,
})
# if "test" in base_url:
#     bit.urls['api'] = bit.urls['test']

while True:
    for binSize_i in range(len(binSizes)):

        # 매수 매도 추세 찾기위한 크롤링
        quote_path = "/quote"
        headers = {"Accept": "application/json"}
        data = {
            "symbol": "XBTUSD",
            "count": "1",
            "reverse": "true"
        }
        prices = requests.get(base_url + quote_path,
                              headers=headers, data=data).json()

        is_bidPrice = prices[-1]["bidSize"] > prices[-1]["askSize"]
        bidPrice = prices[-1]["bidPrice"]  # 매수 호가
        askPrice = prices[-1]["askPrice"]  # 매도 호가

        # if is_bidPrice:
        #     print(
        #         f"매수추세 bidPrice diff : {prices[-1]['bidSize'] - prices[-1]['askSize']}")
        # else:
        #     print(
        #         f"매도추세 askPrice diff : {prices[-1]['askSize'] - prices[-1]['bidSize']}")

        print(f"binSize : {binSizes[binSize_i]}")

        path = "/trade/bucketed"  # "/history"
        symbol = "XBTUSD"
        data = {
            "symbol": symbol,
            "count": "100",
            "reverse": "true",
            "binSize": binSizes[binSize_i]
        }
        raw_data = requests.get(base_url + path,
                                headers=headers, data=data).json()

        if raw_data[0]["timestamp"] > raw_data[1]["timestamp"]:
            data = pd.DataFrame(raw_data)[::-1]
        else:
            data = pd.DataFrame(raw_data)

        # fig = plt.figure(figsize=(12, 8))
        # ax = fig.add_subplot(111)

        data = data.rename(columns={"timestamp": "date"})

        data['avg20'] = data['close'].rolling(window=20).mean()
        data['stddev'] = data['close'].rolling(window=20).std()
        data['ubb'] = data['avg20'] + 2 * data['stddev']  # 상단밴드
        data['lbb'] = data['avg20'] - 2 * data['stddev']  # 하단밴드

        # 볼린저 밴드 탈출 추격롱
        if not is_bought_upper_ubb[binSize_i] and data["close"][0] > data['ubb'][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
                #                  side='buy', amount=100, price=askPrice)
                is_bought_upper_ubb[binSize_i] = True
                send_message(f"{binSizes[binSize_i]} 볼린저 밴드 롱탈출")
            except:
                print("롱 입성 시도")

        # 음전하거나 볼린저 입성할때 팖
        if is_bought_upper_ubb[binSize_i] and data["close"][0] < data["open"][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='limit',
                #                  side='sell', amount=100, price=bidPrice)
                # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": bidPrice},
                #                  side='sell', amount=100, price=bidPrice)
                is_bought_upper_ubb[binSize_i] = False
                send_message(f"{binSizes[binSize_i]} 볼린저 롱탈출 및 음전")
            except:
                print("롱 판매 시도")

        # 볼린저 밴드 탈출 추격숏
        if not is_bought_lower_lbb[binSize_i] and data["close"][0] < data['lbb'][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
                #                  side='sell', amount=100, price=bidPrice)
                is_bought_lower_lbb[binSize_i] = True
                send_message(f"{binSizes[binSize_i]} 볼린저 밴드 숏탈출")
            except:
                print("숏 입성 시도")

        # 양전하거나 볼린저 입성할때 삼
        if is_bought_lower_lbb[binSize_i] and data["close"][0] > data["open"][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='limit',
                #                  side='buy', amount=100, price=askPrice)
                # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": askPrice},
                #                  side='buy', amount=100, price=askPrice)
                send_message(f"{binSizes[binSize_i]} 볼린저 밴드 숏탈출 및 양전")
                is_bought_lower_lbb[binSize_i] = False
            except:
                print("숏 판매 시도")
        # 볼린저 밴드 탈출 추격매수 끝

        # 회귀 매수

        # plt.plot(data["date"], data["avg20"], color="orange")
        # plt.plot(data["date"], data["ubb"], color="red")
        # plt.plot(data["date"], data["lbb"], color="blue")

        # mpl_finance.candlestick2_ohlc(ax, opens=data['open'], highs=data['high'],
        #                               lows=data['low'], closes=data['close'], width=0.5, colorup='r', colordown='b')

        # plt.show()
        time.sleep(3)
    time.sleep(60)

# %%
