# %%
import ccxt
from bitmex import bitmex
import time
from datetime import datetime
import calendar
import requests
import pandas as pd
import webbrowser


def rsicheck(symbol, test, api_key, api_secret, test_api_key, test_api_secret):
    base_url = "https://www.bitmex.com/api/v1"
    test_base_url = "https://testnet.bitmex.com/api/v1"
    if test:
        client = bitmex(test=test, api_key=test_api_key,
                        api_secret=test_api_secret)
    else:
        client = bitmex(test=test, api_key=api_key, api_secret=api_secret)
    symbol = symbol
    now = datetime.now()
    print(now)

    unixtime = calendar.timegm(now.utctimetuple())

    since = unixtime - 60 * 60 * 24 * 5

    param = {"period": 1, "from": since, "to": unixtime}

    if test:
        urlcheck = "https://testnet.bitmex.com/api/udf/history?symbol=" + \
            symbol + "&resolution={period}&from={from}&to={to}"
    else:
        urlcheck = "https://www.bitmex.com/api/udf/history?symbol=" + \
            symbol + "&resolution={period}&from={from}&to={to}"
    url = urlcheck.format(**param)
    res = requests.get(url)
    data = res.json()

    df = pd.DataFrame({
        "timestamp": data["t"],
        "open": data["o"],
        "high": data["h"],
        "low": data["l"],
        "close": data["c"],
        "volume": data["v"],
    }, columns=["timestamp", "open", "high", "low", "close", "volume"])

    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

    df = df.set_index("datetime")

    df = df.resample("1T").agg({
        "timestamp": "first",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })

    def rsi(ohlc: pd.DataFrame, period: int = 14) -> pd.Series:

        delta = ohlc["close"].diff()

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")

    rsi = rsi(df, 14)[-1]

    print('rsi: ', rsi)

    if test:
        urlcheck2 = "https://testnet.bitmex.com/api/v1/orderBook/L2?symbol=" + symbol + "&depth=1"
    else:
        urlcheck2 = "https://www.bitmex.com/api/v1/orderBook/L2?symbol=" + symbol + "&depth=1"

    response = requests.get(urlcheck2).json()

    bidprice = response[1]['price']
    askprice = response[0]['price']

    print(bidprice, askprice)

    unrealizedbalance = client.User.User_getMargin().result()[
        0]['marginBalance'] / (100000000)
    unrealizedbalanceusd = round(bidprice * unrealizedbalance, 0)

    ordersize = round(unrealizedbalanceusd, 0)

    textid = 'rsi'

    bit = ccxt.bitmex({
        'apiKey': test_api_key,
        'secret': test_api_secret,
    })
    bit.urls['api'] = bit.urls['test']

    if rsi > 80:
        try:

            price = askprice
            price2 = askprice - 11

            bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
                             side='sell', amount=ordersize, price=price)

            bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": price + 0.5},
                             side='buy', amount=ordersize, price=price2)

            # sellorder = client.Order.Order_new(symbol=symbol, ordType='Limit', price=price, orderQty=ordersize,
            #                                    side='Sell', text=textid).result()

            # sellorderprofit = client.Order.Order_new(symbol=symbol, ordType='StopLimit', stopPx=price + 0.5,
            #                                          price=price2, orderQty=ordersize, side='Buy', text=textid,
            #                                          execInst='LastPrice').result()

            print('rsi sell')
            time.sleep(1)

        except:
            pass

    if rsi < 20:
        try:

            price = bidprice
            price2 = bidprice + 11

            bit.create_order(symbol='XBTUSD', type='limit', params={"leverage": 1},
                             side='buy', amount=ordersize, price=price)

            bit.create_order(symbol='XBTUSD', type='StopLimit', params={"stopPx": price - 0.5, "leverage": 5},
                             side='sell', amount=ordersize, price=price2)
            # buyorder = client.Order.Order_new(symbol=symbol, ordType='Limit', price=price, orderQty=ordersize,
            #                                   side='Buy', text=textid).result()

            # buyorderprofit = client.Order.Order_new(symbol=symbol, ordType='StopLimit', stopPx=price - 0.5,
            #                                         price=price2, orderQty=ordersize, side='Sell', text=textid,
            #                                         execInst='LastPrice').result()
            print('rsi buy')
            time.sleep(1)
        except:
            pass

    print(11)
    return


# test_api_key = ""
# test_api_secret = ""
# api_key = ""
# api_secret = ""

# while True:
#     try:
#         rsicheck('XBTUSD', test=True, api_key=api_key, test_api_key=test_api_key,
#                  api_secret=api_secret, test_api_secret=test_api_secret)
#         time.sleep(1)
#     except:
#         pass
# rsicheck('XBTUSD')


# text = rsicheck('XBTUSD', test=True, api_key=api_key, test_api_key=test_api_key,
#                 api_secret=api_secret, test_api_secret=test_api_secret)

# %%

# %%
