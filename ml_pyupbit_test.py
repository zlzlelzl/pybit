# %%
from api_key import *
import ccxt
from pyTelegram import send_message
import mpl_finance
# import pandas_datareader.data as web
# import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import requests
import tensorflow as tf
import seaborn as sns
import pyupbit
from get_price_data_from_upbit import get_price_data_from_upbit

# test_api_key = ""
# test_api_secret = ""
# api_key = ""
# api_secret = ""

# base_url = "https://www.bitmex.com/api/v1"
# base_url = "https://testnet.bitmex.com/api/v1"

# curl -X GET --header 'Accept: application/json' 'https://www.bitmex.com/api/v1/quote?&count=100&'

# path = "/trade/bucketed"  # "/history"
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

raw_data = get_price_data_from_upbit(interval="minute1", count=1000)

binSizes = ["1m", "5m", "1h", "1d"]

bought_upper_ubb = [[] for _ in range(len(binSizes))]
bought_upper_date = [[] for _ in range(len(binSizes))]
sold_upper_ubb = [[] for _ in range(len(binSizes))]
sold_upper_date = [[] for _ in range(len(binSizes))]
bought_lower_ubb = [[] for _ in range(len(binSizes))]
bought_lower_date = [[] for _ in range(len(binSizes))]
sold_lower_ubb = [[] for _ in range(len(binSizes))]
sold_lower_date = [[] for _ in range(len(binSizes))]

is_bought_upper_ubb = [0] * len(binSizes)
is_bought_lower_lbb = [0] * len(binSizes)
is_bought_regression_ubb = False
is_bought_regression_lbb = False
upper_ubb_length = [0] * len(binSizes)
lower_lbb_length = [0] * len(binSizes)
ubb_sum = 0
lbb_sum = 0
max_is_bought_upper_ubb = [0] * len(binSizes)
max_is_bought_lower_lbb = [0] * len(binSizes)
maintain_indices_upper = [0] * len(binSizes)
maintain_indices_lower = [0] * len(binSizes)
is_bought_upper_4ubb = [0] * len(binSizes)
is_bought_lower_4lbb = [0] * len(binSizes)
count_upper_4ubb = [0] * len(binSizes)
count_lower_4lbb = [0] * len(binSizes)


is_bought_upper_ubb = [False] * len(binSizes)
is_bought_lower_lbb = [False] * len(binSizes)
is_bought_ubb_cross = False
is_bought_lbb_cross = False

# bit = ccxt.bitmex({
#     'apiKey': api_key,
#     'secret': api_secret,
# })
# if "test" in base_url:
#     bit.urls['api'] = bit.urls['test']

for binSize_i in range(len(binSizes)):
    # quote_path = "/quote"
    # headers = {"Accept": "application/json"}
    # data = {
    #     "symbol": "XBTUSD",
    #     "count": "1",
    #     "reverse": "true"
    # }
    # prices = requests.get(base_url + quote_path,
    #                       headers=headers, data=data).json()

    # is_bidPrice = prices[-1]["bidSize"] > prices[-1]["askSize"]
    # bidPrice = prices[-1]["bidPrice"]  # ?????? ??????
    # askPrice = prices[-1]["askPrice"]  # ?????? ??????

    # if is_bidPrice:
    #     print(
    #         f"???????????? bidPrice diff : {prices[-1]['bidSize'] - prices[-1]['askSize']}")
    # else:
    #     print(
    #         f"???????????? askPrice diff : {prices[-1]['askSize'] - prices[-1]['bidSize']}")

    # print(f"binSize : {binSizes[binSize_i]}")

    # path = "/trade/bucketed"  # "/history"
    # symbol = "XBTUSD"
    # data = {
    #     "symbol": symbol,
    #     "count": "100",
    #     "reverse": "true",
    #     "binSize": binSizes[binSize_i]
    # }
    # raw_data = requests.get(base_url + path,
    #                         headers=headers, data=data).json()

    if raw_data[0]["timestamp"] > raw_data[1]["timestamp"]:
        data = pd.DataFrame(raw_data)[::-1]
    else:
        data = pd.DataFrame(raw_data)

    # fig = plt.figure(figsize=(12, 8))
    # ax = fig.add_subplot(111)

    data = data.rename(columns={"timestamp": "date"})

    data['avg20'] = data['close'].rolling(window=20).mean()
    data['stddev'] = data['close'].rolling(window=20).std()
    data['ubb'] = data['avg20'] + 2 * data['stddev']  # ????????????
    data['lbb'] = data['avg20'] - 2 * data['stddev']  # ????????????

    # ????????? ?????? ?????? ?????????
    if not is_bought_upper_ubb[binSize_i] and data["close"][0] > data['ubb'][0]:
        try:
            # bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
            #                  side='buy', amount=100, price=askPrice)
            is_bought_upper_ubb[binSize_i] = True
            send_message(f"{binSizes[binSize_i]} ????????? ?????? ?????????")
        except:
            print("??? ?????? ??????")

    # ??????????????? ????????? ???????????? ???
    elif is_bought_upper_ubb[binSize_i] and data["close"][0] < data["open"][0]:
        try:
            # bit.create_order(symbol='XBTUSD', type='limit',
            #                  side='sell', amount=100, price=bidPrice)
            # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": bidPrice},
            #                  side='sell', amount=100, price=bidPrice)
            is_bought_upper_ubb[binSize_i] = False
            send_message(f"{binSizes[binSize_i]} ????????? ????????? ??? ??????")
        except:
            print("??? ?????? ??????")

    # ????????? ?????? ?????? ?????????
    if not is_bought_lower_lbb[binSize_i] and data["close"][0] < data['lbb'][0]:
        try:
            # bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
            #                  side='sell', amount=100, price=bidPrice)
            is_bought_lower_lbb[binSize_i] = True
            send_message(f"{binSizes[binSize_i]} ????????? ?????? ?????????")
        except:
            print("??? ?????? ??????")

    # ??????????????? ????????? ???????????? ???
    elif is_bought_lower_lbb[binSize_i] and data["close"][0] > data["open"][0]:
        try:
            # bit.create_order(symbol='XBTUSD', type='limit',
            #                  side='buy', amount=100, price=askPrice)
            # bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": askPrice},
            #                  side='buy', amount=100, price=askPrice)
            send_message(f"{binSizes[binSize_i]} ????????? ?????? ????????? ??? ??????")
            is_bought_lower_lbb[binSize_i] = False
        except:
            print("??? ?????? ??????")
    # ????????? ?????? ?????? ???????????? ???

    # ?????? ??????

    # plt.plot(data["date"], data["avg20"], color="orange")
    # plt.plot(data["date"], data["ubb"], color="red")
    # plt.plot(data["date"], data["lbb"], color="blue")

    # mpl_finance.candlestick2_ohlc(ax, opens=data['open'], highs=data['high'],
    #                               lows=data['low'], closes=data['close'], width=0.5, colorup='r', colordown='b')

    # plt.show()
# %%
# ????????? ??????


def MinMaxScaler(data):
    denom = np.max(data, 0)-np.min(data, 0)
    nume = data-np.min(data, 0)
    return nume/denom

# ????????? ???????????? ??????


def back_MinMax(data, value):
    diff = np.max(data, 0)-np.min(data, 0)
    back = value * diff + np.min(data, 0)
    return back


# , delimiter=",", skiprows=0+1+1
# ????????? ????????????

raw_xy = pd.read_csv("data_minute15_count_1000.csv")
stored_xy = [[] for _ in range(5)]
for c, col in enumerate([0, 1, 2, 4, 3]):
    for row in range(len(raw_xy)):
        stored_xy[c].append(raw_xy[raw_xy.columns[col+1]][row])

stored_xy = np.array(stored_xy)
stored_xy = stored_xy.T
if 1:
    i = 1000
    xy = stored_xy[:i]

    plt.plot(xy[:, 4])  # ?????? ??????

    seqLength = 7  # window size
    dataDim = 5  # ??????, ??????, ??????, ????????? , ??????
    hiddenDim = 10
    outputDim = 1
    lr = 0.01
    iterations = 500

    trainSize = int(len(xy)-30)
    trainSet = xy[0:trainSize]
    testSet = xy[trainSize-seqLength:]

    trainSet = MinMaxScaler(trainSet)
    testSet = MinMaxScaler(testSet)

    # 7????????? 5?????? ?????????(??????, ??????, ??????, ??????, ?????????)??? ????????????
    # ?????? ?????? ?????? ????????? ???????????? ????????? ??????

    def buildDataSet(timeSeries, seqLength):
        xdata = []
        ydata = []
        for i in range(0, len(timeSeries)-seqLength):
            tx = timeSeries[i:i+seqLength, :-1]
            ty = timeSeries[i+seqLength, [-1]]
            xdata.append(tx)
            ydata.append(ty)
        return np.array(xdata), np.array(ydata)

    trainX, trainY = buildDataSet(trainSet, seqLength)
    testX, testY = buildDataSet(testSet, seqLength)

    # ?????? ??????

    # First, let's define a RNN Cell, as a layer subclass.
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential()

    model.add(layers.LSTM(units=10,
                          activation='tanh',
                          input_shape=[7, 4]))

    model.add(layers.Dense(1))

    model.summary()

    # ?????? ???????????? ??????
    model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    # ?????? ????????????
    hist = model.fit(trainX, trainY, epochs=1000, batch_size=16)

    # 7 ?????? ??????
    xhat = testX
    yhat = model.predict(xhat)
    print(testY)
    print(yhat)

    print("Evaluate : {}".format(np.average((yhat - testY)**2)))

    # ?????? ????????? ????????????
    predict1 = back_MinMax(xy[trainSize-seqLength:, [-1]], yhat)
    # actual = back_MinMax
    actual = back_MinMax(xy[trainSize-seqLength:, [-1]], testY)
    print("?????????", predict1)
    print("?????????", actual)

    print(predict1.shape)
    print(actual.shape)

    plt.figure()
    print(i)
    plt.plot(predict1[:30], label="predict_RNN")
    plt.plot(actual[:30], label="actual")

    plt.legend(prop={'size': 20})
# %%
trainSize
# %%
predict1
# %%
