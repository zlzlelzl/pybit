# %%
from datetime import datetime
from api_key import *
from pyTelegram import send_message
import time
from bitmex_websocket import BitMEXWebsocket

base_url = "https://www.bitmex.com/api/v1"

############ 조건 분기 변수 ##########################################################

## 고정 변수 ##

margin_cut_val = 36778.0
two_if_4bb_twice_else_one = 1
fixed_amount = 10000

####################################################################################

while True:
    ws = BitMEXWebsocket(endpoint="wss://ws.bitmex.com/realtime",
                         symbol="XBTUSD", api_key=api_key, api_secret=api_secret)
    instrument = ws.get_instrument()
    bidPrice = float(instrument["bidPrice"])
    askPrice = float(instrument["askPrice"])

    if askPrice - margin_cut_val < 0 or bidPrice - margin_cut_val < 0:
        send_message("청산")
        break

    print(f"{askPrice - margin_cut_val}, {bidPrice - margin_cut_val} - {datetime.now().strftime('%H:%M:%S')}")
    time.sleep(10)
