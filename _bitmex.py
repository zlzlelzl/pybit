# %%
import numpy as np
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
api_key = ""
base_url = "https://www.bitmex.com/api/v1"
#
# curl -X GET --header 'Accept: application/json' 'https://www.bitmex.com/api/v1/quote?&count=100&'

path = "/trade/bucketed"  # "/history"
headers = {"Accept": "application/json"}
data = {
    "api-key": api_key,
    "symbol": "XBTUSD",
    "count": "1000",
    "reverse": "False"
}
data["binSize"] = "1m"

# %%
raw_data = requests.get(base_url + path, headers=headers, data=data).json()
# # %%
data = pd.DataFrame(raw_data)
# # %%
# usd_data = list(filter(lambda x: "USD" in x["symbol"], data))

# # %%
# usd_data
data

# mbb = 중심선 = 주가의 20 기간 이동평균선 = clo20
# ubb = 상한선 = 중심선 + 주가의 20기간 표준편차 * 2
# lbb = 하한선 = 중심선 – 주가의 20기간 표준편차 * 2
# perb = %b = (주가 – 하한선) / (상한선 – 하한선) = (close - lbb) / (ubb - lbb)
# bw = 밴드폭 (Bandwidth) = (상한선 – 하한선) / 중심선 = (ubb - lbb) / mbb
# https://wikidocs.net/87171 볼린저밴드

# https://www.bitmex.com/api/explorer/#/
# %%

# 볼린저밴드 맞는지 확인해봐야댐
# 1분봉, 15분봉
