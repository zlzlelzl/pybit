# %%
import schedule
from datetime import datetime
from api_key import *
import ccxt
from pyTelegram import send_message
# import mpl_finance
# import pandas_datareader.data as web
# import datetime
# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import requests
from bitmex_websocket import BitMEXWebsocket
pd.set_option('mode.chained_assignment',  None)

# api_key = ""
# api_secret = ""
# api_key = ""  # test
# api_secret = ""  # test

base_url = "https://www.bitmex.com/api/v1"
# base_url = "https://testnet.bitmex.com/api/v1"

# curl -X GET --header 'Accept: application/json' 'https://www.bitmex.com/api/v1/quote?&count=100&'

binSizes = ["1m"]  # ,"5m", "1h", "1d"]

############ 조건 분기 변수 ##########################################################

## 선언 변수 ##

is_bought_upper_ubb = [False] * len(binSizes)
is_bought_lower_lbb = [False] * len(binSizes)
is_bought_ubb_cross = False
is_bought_lbb_cross = False
is_additional_purchase = [False] * len(binSizes)
is_opened = False

## 고정 변수 ##

two_if_4bb_twice_else_one = 1
fixed_amount = 10000

####################################################################################

bit = ccxt.bitmex({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})
# if "test" in base_url:
#     bit.urls['api'] = bit.urls['test']

ws = BitMEXWebsocket(endpoint="wss://ws.bitmex.com/realtime",
                     symbol="XBTUSD", api_key=api_key, api_secret=api_secret)


def fnRSI(m_Df, m_N):

    U = np.where(m_Df.diff(1) > 0, m_Df.diff(1), 0)
    D = np.where(m_Df.diff(1) < 0, m_Df.diff(1) * (-1), 0)

    AU = pd.DataFrame(U).rolling(window=m_N, min_periods=m_N).mean()
    AD = pd.DataFrame(D).rolling(window=m_N, min_periods=m_N).mean()
    RSI = AU.div(AD+AU) * 100
    return RSI


def order_module(side, want_qty):
    try:
        while True:
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


def ohlcv_to_file(binSize_i):
    binSize_i = 0
    raw_df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=30,
                             timeframe=binSizes[binSize_i])
    columns = ["date", "open", "high", "low", "close", "volume"]

    df = pd.DataFrame(raw_df, columns=columns)
    df.to_csv("ohlcv_30.csv")


schedule.every().minute.at(":02").do(ohlcv_to_file, 0)


# while True:
if 1:
    for binSize_i in range(len(binSizes)):
        ## 고정 변수 ##
        two_if_4bb_twice_else_one = 1
        amount = fixed_amount

        # 매수 매도 추세 찾기위한 크롤링
        quote_path = "/quote"
        headers = {"Accept": "application/json"}
        data = {
            "symbol": "XBTUSD",
            "count": "1",
            "reverse": "true"
        }
        # try:
        #     prices = requests.get(base_url + quote_path,
        #                           headers=headers, data=data).json()
        #     is_bidPrice = prices[-1]["bidSize"] > prices[-1]["askSize"]
        #     bidPrice = prices[-1]["bidPrice"]  # 구매요청가
        #     askPrice = prices[-1]["askPrice"]  # 판매요청가
        # except:
        if 1:
            instrument = ws.get_instrument()
            is_bidPrice = 1 if instrument["lastTickDirection"] == "ZeroPlusTick" else 0
            bidPrice = float(instrument["bidPrice"])
            askPrice = float(instrument["askPrice"])

        # path = "/trade/bucketed"  # "/history"
        # symbol = "XBTUSD"
        # data = {
        #     "symbol": symbol,
        #     "count": "100",
        #     "reverse": "true",
        #     "binSize": binSizes[binSize_i]
        # }
        # raw_df = requests.get(base_url + path,
        #                       headers=headers, data=data).json()

        schedule.run_pending()

        df = pd.read_csv("ohlcv_30.csv")

        # 파일로 쓰기

        new_data = {
            'close': float(ws.recent_trades()[-1]["price"]),
        }
        df.loc[30] = new_data  # df 크기 고정
        df = df.set_index(keys=reversed(df.index))

        # df['avg20'] = df['close'].rolling(window=20).mean()
        # df['stddev'] = df['close'].rolling(window=20).std()
        # df['ubb'] = df['avg20'] + 2 * df['stddev']  # 상단밴드
        # df['lbb'] = df['avg20'] - 2 * df['stddev']  # 하단밴드
        # df['4ubb'] = df['avg20'] + 4 * df['stddev']  # 상단밴드
        # df['4lbb'] = df['avg20'] - 4 * df['stddev']  # 상단밴드

        rsi = fnRSI(df["close"], 13)[30]

        print(rsi)

        # 1번 4시그마 구매 2시그마 판매
        # ss = time.process_time()
        # ee = time.process_time()
        # print(ee-ss)
        # 구매 시작
        # if not is_opened:
        #     if not is_bought_upper_ubb[binSize_i] and askPrice > df['4ubb'][0]:
        #         try:
        #             # 싹 다 고쳐야됨 + 모듈화
        #             # bit.create_order(symbol='XBTUSD', type='limit',
        #             #                  side='sell', amount=amount, price=askPrice)
        #             # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": askPrice},
        #             #                  side='sell', amount=amount, price=bidPrice+1)
        #             is_bought_upper_ubb[binSize_i] = True

        #             send_message(f"{binSizes[binSize_i]} 4ubb 숏 구매")
        #         except:
        #             print("숏 입성 시도")

        #     # 4lbb 롱 구매
        #     if not is_bought_lower_lbb[binSize_i] and bidPrice < df['4lbb'][0]:
        #         try:
        #             # bit.create_order(symbol='XBTUSD', type='limit',
        #             #                  side='buy', amount=amount, price=bidPrice)
        #             # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": bidPrice},
        #             #                  side='buy', amount=amount, price=askPrice-1)
        #             is_bought_lower_lbb[binSize_i] = True
        #             send_message(f"{binSizes[binSize_i]} 4lbb 롱 구매")
        #         except:
        #             print("롱 입성 시도")

        #     # # 시간 줄이기
        #     # if is_bought_upper_ubb[binSize_i] or is_bought_lower_lbb[binSize_i]:
        #     #     if len(bit.fetch_open_orders()) < 2:
        #     #         fetch_position = bit.fetch_positions()
        #     #         if fetch_position[0]["isOpen"]:

        #     #             # fetch_position 파일 쓰기
        #     #             bit.cancel_all_orders()
        #     #             is_opened = True

        #     #         # StopLimit으로도 못샀으면 그냥 포기
        #     #         # 요청가격보다 10 차이날때(20이 본전이라)
        #     #         else:
        #     #             if (is_bought_upper_ubb[binSize_i] and df['4ubb'][0] - 10) or \
        #     #                     (is_bought_lower_lbb[binSize_i] and df['4lbb'][0] + 10):
        #     #                 bit.cancel_all_orders()
        #     #                 is_bought_upper_ubb[binSize_i] = False
        #     #                 is_bought_lower_lbb[binSize_i] = False

        # # 구매했으면 판매될때까지 안빠져나오기
        # else:  # is_opened
        #     break
        # if not fetch_position[0]["isOpen"]:
        #     is_opened = False
        #     bidPrice 구매요청가
        #     askPrice 판매요청가

        # 1분 뒤에 4bb면 x2해서 사고 1분 추가
        # 1분 뒤에 2~4bb면서 가격이 올랐으면 x1 사고 1분추가, 가격이 내렸으면 팔기
        # 1분 뒤에 0~2bb면 0에 리밋, 2bb에 스탑 리밋 및 청산

        # 4bb가 얼마고 구매요청 가격(내가 바로 살 수 있는 가격)이 얼마인지 표현

        # 오더, 포지션 정리를 위한 대전제
        # if is_bought_upper_ubb[binSize_i] or is_bought_lower_lbb[binSize_i]:

        #     # # 1분 기다리기
        #     # over_60s += 2
        #     # if over_60s > 60:
        #     if not is_additional_purchase[binSize_i]:
        #         if is_bought_upper_ubb[binSize_i]:
        #             if bidPrice > df['4ubb'][0]:
        #                 is_additional_purchase[binSize_i] = True
        #                 over_60s = 0
        #             elif bidPrice < df['20avg'][0]:
        #                 is_bought_upper_ubb[binSize_i] = False
        #             else:
        #                 if float(fetch_position[0]["avgEntryPrice"]) <= bidPrice:
        #                     is_bought_upper_ubb[binSize_i] = False
        #                 else:
        #                     is_additional_purchase[binSize_i] = True
        #                     over_60s = 0

        #         elif is_bought_lower_lbb[binSize_i]:
        #             if askPrice < df['4lbb'][0]:
        #                 is_additional_purchase[binSize_i] = True
        #                 over_60s = 0
        #             elif askPrice > df['20avg'][0]:
        #                 is_bought_lower_lbb[binSize_i] = False
        #             else:
        #                 if float(fetch_position[0]["avgEntryPrice"]) >= askPrice:
        #                     is_bought_lower_lbb[binSize_i] = False
        #                 else:
        #                     is_additional_purchase[binSize_i] = True
        #                     over_60s = 0

        #     # 추가 상승 구매 처리
        #     # 다시 4bb 넘으면 x2 재구매
        #     # 2~4bb면서 산가격 넘으면 재구매
        #     else:
        #         if is_bought_upper_ubb[binSize_i]:
        #             if bidPrice > df['4ubb'][0]:
        #                 two_if_4bb_twice_else_one = 2

        #             bit.create_order(symbol='XBTUSD', type='limit',
        #                              side='buy', amount=100 * two_if_4bb_twice_else_one, price=bidPrice)

        #             two_if_4bb_twice_else_one = 1
        #             over_60s = 0

        #         elif is_bought_lower_lbb[binSize_i]:
        #             if askPrice > df['4lbb'][0]:
        #                 two_if_4bb_twice_else_one = 2

        #             bit.create_order(symbol='XBTUSD', type='limit',
        #                              side='sell', amount=100 * two_if_4bb_twice_else_one, price=askPrice)

        #             two_if_4bb_twice_else_one = 1
        #             over_60s = 0

        #             # 오더, 포지션 정리
        # else:
        #     is_opened = False

        # # 1분동안 ubb 근처도 못갔으면 지정가 바꿔가면서 청산
        # if over_60s > 60:
        #     over_60s = 0
        #     bit.cancel_all_orders()
        #     if is_bought_upper_ubb[binSize_i]:
        #         bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": bidPrice},
        #                          side='buy', amount=100, price=bidPrice)
        #     if is_bought_lower_lbb[binSize_i]:
        #         bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": df['ubb'][0]},
        #                          side='buy', amount=100, price=bidPrice)

        # print(
        #     f"{int(df['4ubb'][0] - askPrice)} {int(bidPrice - df['4lbb'][0])} - {datetime.now().strftime('%H:%M:%S')}")
        # plt.plot(df["date"], df["avg20"], color="orange")
        # plt.plot(df["date"], df["ubb"], color="red")
        # plt.plot(df["date"], df["lbb"], color="blue")

        # mpl_finance.candlestick2_ohlc(ax, opens=df['open'], highs=df['high'],
        #                               lows=df['low'], closes=df['close'], width=0.5, colorup='r', colordown='b')

        # plt.show()


# %%
# new_df = df['close'].rolling(window=14).method
# new_df


# %%
fnRSI(df["close"], 30-14+1)
# %%
df["close"]

45.35
