# %%
from bitmex_websocket import BitMEXWebsocket
from api_key import *
import ccxt
from pyTelegram import send_message
import mpl_finance
# import pandas_datareader.data as web
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import requests
pd.set_option('mode.chained_assignment',  None)
pd.set_option('display.max_seq_items', None)
pd.set_option('display.max_rows', 500)

# test_api_key = ""
# test_api_secret = ""
# api_key = ""
# api_secret = ""

# base_url = "https://www.bitmex.com/api/v1"
base_url = "https://testnet.bitmex.com/api/v1"

bought_upper_ubb = []
bought_upper_date = []
sold_upper_ubb = []
sold_upper_date = []
bought_lower_ubb = []
bought_lower_date = []
sold_lower_ubb = []
sold_lower_date = []

# "1m"
binSizes = ["1m"]  # ,"5m", "1h", "1d"]

is_bought_upper_ubb = [False] * len(binSizes)
is_bought_lower_lbb = [False] * len(binSizes)
is_bought_ubb_cross = False
is_bought_lbb_cross = False
count_bought_upper_ubb = [0] * len(binSizes)
count_bought_lower_lbb = [0] * len(binSizes)

bit = ccxt.bitmex({
    'apiKey': api_key,
    'secret': api_secret,
    # 'enableRateLimit': True,
})
if "test" in base_url:
    bit.urls['api'] = bit.urls['test']

ws = BitMEXWebsocket(endpoint="wss://ws.testnet.bitmex.com/realtime",
                     symbol="XBTUSD", api_key=api_key, api_secret=api_secret)

temp_count = 0
renew_60s = 60
# while True:
if 1:
    for binSize_i in range(len(binSizes)):

        # 매수 매도 추세 찾기위한 크롤링
        quote_path = "/quote"
        headers = {"Accept": "application/json"}
        data = {
            "symbol": "XBTUSD",
            "count": "1",
            "reverse": "true"
        }

        try:
            prices = requests.get(base_url + quote_path,
                                  headers=headers, data=data).json()
            is_bidPrice = prices[-1]["bidSize"] > prices[-1]["askSize"]
            bidPrice = prices[-1]["bidPrice"]  # 구매요청가
            askPrice = prices[-1]["askPrice"]  # 판매요청가
        except:
            prices = bit.fetch_order_book(symbol="BTC/USD:BTC", limit=1)
            is_bidPrice = prices["bids"][0][1] > prices["asks"][0][1]
            bidPrice = prices["bids"][0][0]
            askPrice = prices["asks"][0][0]

        print(bidPrice, askPrice)

        # if renew_60s >= 60:
        if 1:
            # renew_60s = 0

            path = "/trade/bucketed"  # "/history"
            symbol = "XBTUSD"
            data = {
                "symbol": symbol,
                "count": "30",
                "reverse": "true",
                "binSize": binSizes[binSize_i]
            }
            # try:
            #     raw_df = requests.get(base_url + path,
            #                           headers=headers, data=data).json()

            #     if raw_df[0]["timestamp"] > raw_df[1]["timestamp"]:
            #         df = pd.DataFrame(raw_df)[::-1]
            #     else:
            #         df = pd.DataFrame(raw_df)

            #     df = df.rename(columns={"timestamp": "date"})
            # except:
            #     raw_df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=30,
            #                              timeframe=binSizes[binSize_i])
            #     columns = ["date", "open", "high", "low", "close", "volume"]
            #     df = pd.DataFrame(raw_df, columns=columns)
            # if 1:
            #     #     print(11)
            #     raw_df = requests.get(base_url + path,
            #                           headers=headers, data=data).json()
            #     if raw_df[0]["timestamp"] > raw_df[1]["timestamp"]:
            #         df = pd.DataFrame(raw_df)[::-1]
            #     else:
            #         df = pd.DataFrame(raw_df)
            #     df = df.rename(columns={"timestamp": "date"})
            #     df["close"][0] = (bidPrice + askPrice) / 2
            # else:
            if 1:

                raw_df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=100,
                                         timeframe=binSizes[binSize_i])
                columns = ["date", "open", "high", "low", "close", "volume"]
                df = pd.DataFrame(raw_df, columns=columns)
                df["date"] = df["date"].map(
                    lambda x: datetime.fromtimestamp(x // 1000))
                df["close"][-1] = (bidPrice + askPrice) / 2

        df['avg20'] = df['close'].rolling(window=20).mean()
        df['stddev'] = df['close'].rolling(window=20).std()
        df['ubb'] = df['avg20'] + 2 * df['stddev']  # 상단밴드
        df['lbb'] = df['avg20'] - 2 * df['stddev']  # 하단밴드
        df['4ubb'] = df['avg20'] + 4 * df['stddev']  # 상단밴드
        df['4lbb'] = df['avg20'] - 4 * df['stddev']  # 상단밴드

        # 1번 4시그마 구매 2시그마 판매
        # 4ubb 숏 구매
        if not is_bought_upper_ubb[binSize_i] and askPrice > df['ubb'][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": df['ubb'][0]},
                #                  side='sell', amount=100, price=askPrice)
                # bit.create_order(symbol='XBTUSD', type='market', params={"leverage": 100},
                #                  side='sell', amount=100)
                is_bought_upper_ubb[binSize_i] = True
                send_message(f"{binSizes[binSize_i]} 4ubb 숏 구매")
            except:
                print("숏 입성 시도")

        # 4ubb 숏 판매
        if is_bought_upper_ubb[binSize_i]:
            count_bought_upper_ubb[binSize_i] += 1
            if bidPrice < df["ubb"][0] or count_bought_upper_ubb[binSize_i] > 12:
                count_bought_upper_ubb[binSize_i] = 0
                try:
                    # bit.create_order(symbol='XBTUSD', type='market', params={"leverage": 100},
                    #                  side='buy', amount=100)
                    is_bought_upper_ubb[binSize_i] = False
                    send_message(f"{binSizes[binSize_i]} 4ubb 숏 판매")
                    temp_count += 1
                except:
                    print("숏 판매 시도")

        # 4lbb 롱 구매
        if not is_bought_lower_lbb[binSize_i] and bidPrice < df['lbb'][0]:
            try:
                # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": df['lbb'][0]},
                #                  side='buy', amount=100, price=bidPrice)
                is_bought_lower_lbb[binSize_i] = True
                send_message(f"{binSizes[binSize_i]} 4lbb 롱 구매")
            except:
                print("롱 입성 시도")

        # 4lbb 롱 판매
        if is_bought_lower_lbb[binSize_i]:
            count_bought_lower_lbb[binSize_i] += 1
            if askPrice > df["lbb"][0] or count_bought_lower_lbb[binSize_i] > 12:
                count_bought_lower_lbb[binSize_i] = 0
                try:
                    # bit.create_order(symbol='XBTUSD', type='market', params={"leverage": 100},
                    #                  side='sell', amount=100)
                    is_bought_lower_lbb[binSize_i] = False
                    send_message(f"{binSizes[binSize_i]} 4lbb 롱 판매")
                    temp_count += 1
                except:
                    print("롱 판매 시도")

        print(f"binSize : {binSizes[binSize_i]}")

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        plt.plot(df["date"], df["avg20"], color="orange")
        plt.plot(df["date"], df["ubb"], color="red")
        plt.plot(df["date"], df["lbb"], color="blue")
        # print(df)
        mpl_finance.candlestick2_ohlc(ax=ax, opens=df['open'], highs=df['high'],
                                      lows=df['low'], closes=df['close'], width=0.5, colorup='r', colordown='b')

        plt.show()
    renew_60s += 3
    time.sleep(3)

# %%
# bit.fetch_markets({symbol: 'XBTUSD', "leverage": "100"})
# bit.create_order(symbol='XBTUSD', type='market', side='buy', amount=100)
# bit.fetch_balance()
# bit.fetch_open_orders()
# bit.cancel_all_orders()

# 현재가격
# bit.fetch_balance()["BTC"]["free"]

# 지정가, 스탑px 둘다 하고 오픈오더 길이 1되면 걍 다 청산
# bit.create_order(symbol='XBTUSD', type='limit',
#                     side='sell', amount=100, price=bidPrice)


# stopPx를 4bb로, price를 askprice로
ss = time.process_time()

ee = time.process_time()
print(ee-ss)
# %%
# while True:
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)

# if 1:
# df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=100,
#                          timeframe=binSizes[binSize_i])
# columns = ["date", "open", "high", "low", "close", "volume"]
# df = pd.DataFrame(df, columns=columns)
# df["date"] = df["date"].map(
#     lambda x: datetime.fromtimestamp(x/1000))
# print(raw_df)
path = "/trade/bucketed"  # "/history"
symbol = "XBTUSD"
data = {
    "symbol": symbol,
    "count": "100",
    "reverse": "true",
    "binSize": binSizes[binSize_i]
}
raw_df = requests.get(base_url + path,
                      headers=headers, data=data).json()
if raw_df[0]["timestamp"] > raw_df[1]["timestamp"]:
    df = pd.DataFrame(raw_df)[::-1]
else:
    df = pd.DataFrame(raw_df)
df = df.rename(columns={"timestamp": "date"})
df["close"][0] = (bidPrice + askPrice) / 2
df['avg20'] = df['close'].rolling(window=20).mean()
df['stddev'] = df['close'].rolling(window=20).std()
df['ubb'] = df['avg20'] + 2 * df['stddev']  # 상단밴드
df['lbb'] = df['avg20'] - 2 * df['stddev']  # 하단밴드
df['4ubb'] = df['avg20'] + 4 * df['stddev']  # 상단밴드
df['4lbb'] = df['avg20'] - 4 * df['stddev']  # 상단밴드
plt.plot(df["date"], df["avg20"], color="orange")
plt.plot(df["date"], df["ubb"], color="red")
plt.plot(df["date"], df["lbb"], color="blue")
mpl_finance.candlestick2_ohlc(ax=ax, opens=df['open'], highs=df['high'],
                              lows=df['low'], closes=df['close'], width=0.5, colorup='r', colordown='b')
plt.show()
# print(df["date"])
# pd.to_datetime(pd.Series(df.TimeReviewed))
# pandas.core.series.Series
# path = "/trade/bucketed"  # "/history"
# symbol = "XBTUSD"
# data = {
#     "symbol": symbol,
#     "count": 10,
#     "reverse": "true",
#     "binSize": binSizes[binSize_i]
# }
# raw_df = requests.get(base_url + path,
#                       headers=headers, data=data).json()
# print(pd.DataFrame(raw_df))

# datetime.fromtimestamp(1644639600)
# .toordinal(1644639600000)

# %%
# bit.create_order(symbol='XBTUSD', type='market', side='sell', amount=100)
# bit.create_order(symbol='XBTUSD', type='limit',
#                  side='buy', price=42462, amount=100)
# len(bit.fetch_positions())+len(bit.fetch_open_orders())
# bit.cancel_all_orders()
# float(bit.fetch_positions()[0]["avgEntryPrice"])
while bit.fetch_positions()[0]["currentQty"] < 1000:
    bit.cancel_all_orders()
    if len(bit.fetch_open_orders()) == 0:
        prices = bit.fetch_order_book(symbol="BTC/USD:BTC", limit=1)
        bidPrice = prices["bids"][0][0]
        askPrice = prices["asks"][0][0]
        bit.create_order(symbol='XBTUSD', type='limit',
                         side='buy', amount=1000, price=askPrice)

# %%
while bit.fetch_positions()[0]["isOpen"]:
    bit.cancel_all_orders()
    if len(bit.fetch_open_orders()) == 0:
        prices = bit.fetch_order_book(symbol="BTC/USD:BTC", limit=1)
        bidPrice = prices["bids"][0][0]
        askPrice = prices["asks"][0][0]
        bit.create_order(symbol='XBTUSD', type='limit',
                         side='sell', amount=1000, price=bidPrice-50)

# %%

# raw_df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=100,
#                          timeframe=binSizes[binSize_i])
# columns = ["date", "open", "high", "low", "close", "volume"]
# df = pd.DataFrame(raw_df, columns=columns)
# # df["date"] = df["date"].map(
# #     lambda x: datetime.fromtimestamp(x // 1000))
# df["close"][-1] = (bidPrice + askPrice) / 2
# df = df.set_index(keys=reversed(df.index))
# bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": "1"},
#                  side='buy', amount=100, price=askPrice)
# len(bit.fetch_positions())
# leverage_path = "/position/leverage"
# requests.post(base_url + leverage_path, headers=headers, data=data).json()
# trade_path = "/trade"
# requests.get(base_url + trade_path, headers=headers, data=data).json()
# wss_url = "https://www.bitmex.com/realtime"
# ws.receive()

# %%


# 싸게 사고 싶어서 싸게 걸어놓음 -> 내가 거는 bid를 낮춤
# 차트의 ask가 높아져 그럼 그때 살꺼야
#
# %%

# %%


def order_module(side, want_qty):
    try:
        while True:
            print(want_qty)
            positions = ws.positions()
            instrument = ws.get_instrument()
            current_qty = int(positions[0]["currentQty"])

            if current_qty == want_qty:
                break

            amount = want_qty - current_qty
            price = instrument["askPrice"] if side == "buy" else instrument["bidPrice"]

            if max(int(positions[0]["openOrderBuyQty"]), int(positions[0]["openOrderSellQty"])) == 0:
                bit.create_order(symbol='XBTUSD', type='limit', params={"timeInForce": "ImmediateOrCancel"},
                                 side=side, amount=amount, price=price)

            time.sleep(0.3)
    except Exception:
        print(Exception)


order_module("buy", -100)
# %%

# %%
current_qty = int(ws.positions()[0]["currentQty"])

instrument = ws.get_instrument()
price = instrument["askPrice"]

bit.create_order(symbol='XBTUSD', type='limit', params={"timeInForce": "ImmediateOrCancel"},
                 side="buy", amount=200, price=price)
# %%
# 스탑에 닿으면
# bit.create_order(symbol='XBTUSD', type='LimitIfTouched', params={"stopPx": bidPrice, "timeInForce": "ImmediateOrCancel"},
#                  side='buy', amount=100, price=askPrice,)

# # 스탑에 닿으면 삭제, price에 닿으면 구매
# bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": bidPrice},
#                  side='buy', amount=100, price=askPrice)

# %%
# ws.positions()
# ws = BitMEXWebsocket(endpoint="wss://ws.bitmex.com/realtime",
#                      symbol="XBTUSD", api_key=api_key, api_secret=api_secret)

# %%


# ws.recent_trades()[-1]
# ws.get_ticker()
# ws.get_instrument()
# prices = bit.fetch_order_book(symbol="BTC/USD:BTC", limit=1)
# is_bidPrice = prices["bids"][0][1] > prices["asks"][0][1]
# bidPrice = prices["bids"][0][0]
# askPrice = prices["asks"][0][0]
ws.get_instrument()

# %%
# a31f698

orderID = bit.fetch_open_orders()[0]["info"]["orderID"]

bit.edit_order(id=orderID, symbol='XBTUSD', type='Limit',
               side='buy', amount=100, price=39576)

# bit.create_order(symbol='XBTUSD', type='Limit',
#                          side='buy', amount=100, price=39461)

# %%
