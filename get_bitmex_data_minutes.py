# %%
from get_price_data_from_upbit import get_price_data_from_upbit
import pyupbit
from pyTelegram import send_message
import ccxt
from datetime import datetime
import matplotlib.pyplot as plt
import mpl_finance
import pandas as pd
import numpy as np
import time
import requests
from sklearn.ensemble import RandomForestClassifier


def get_price_df_from_bitmex(start, end=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')):
    def str_to_timestamp(s):
        return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())

    end = int(str_to_timestamp(end))
    start = int(str_to_timestamp(start))

    url = f"https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution={1}&from={start}&to={end}"
    res = requests.get(url).json()

    return res


raw_df = []
for y in range(2021, 2023):
    for m in range(1, 12+1):
        raw_df.append(pd.DataFrame())
        for d in range(28, 31 + 1):
            try:
                time.sleep(2)
                raw_df[-1] = raw_df[-1].append(pd.DataFrame(get_price_df_from_bitmex(
                    f'{y}-{str(m).rjust(2,"0")}-{str(d).rjust(2,"0")} 09:00:00',
                    f'{y}-{str(m).rjust(2,"0")}-{str(d+1).rjust(2,"0")} 08:59:59')))
            except:
                try:
                    time.sleep(2)
                    raw_df[-1] = raw_df[-1].append(pd.DataFrame(get_price_df_from_bitmex(
                        f'{y}-{str(m).rjust(2,"0")}-{str(d).rjust(2,"0")} 09:00:00',
                        f'{y}-{str(m+1).rjust(2,"0")}-{str(1).rjust(2,"0")} 08:59:59')))

                except:
                    try:
                        print(y, m, d)
                        time.sleep(2)
                        raw_df[-1] = raw_df[-1].append(pd.DataFrame(get_price_df_from_bitmex(
                            f'{y}-{str(m).rjust(2,"0")}-{str(d).rjust(2,"0")} 09:00:00',
                            f'{y+1}-{str(1).rjust(2,"0")}-{str(1).rjust(2,"0")} 08:59:59')))
                    except:
                        pass

for i in range(len(raw_df)):
    raw_df[i].reset_index(drop=True, inplace=True)
    try:
        raw_df[i].columns = ["s", "date", "close",
                             "open", "high", "low", "volume"]
    except:
        pass

send_message('1')
raw_df
# %%
for i in range(len(raw_df)):
    print(raw_df[i]["date"].isnull().sum())
# %%
for i in range(len(raw_df)):
    raw_df[i]["date"].isnull().sum()
# %%
len(raw_df)
# %%
df = pd.read_csv(f"data_bitmex_minute1.csv").drop("Unnamed: 0", axis="columns")
# %%
for i in range(len(raw_df)):
    df = df.append(raw_df[i])
    df = df.sort_values(by=['date'], ascending=True)
    df.reset_index(drop=True, inplace=True)
df = df.drop_duplicates()
df.reset_index(drop=True, inplace=True)
df
# %%
# 순서 및 중복 무결성
now = 0
for i in range(len(df)):
    if now >= df["date"][i]:
        print(i)
        break
    now = df["date"][i]
# %%
# 기간 등차수열 체크
for i in range(2, len(df))[:40000]:
    if df["date"][i] - df["date"][i-1] != df["date"][i-1] - df["date"][i-2]:
        print(i)
        break

# %%

df.to_csv("data_bitmex_minute1.csv")
# %%
# %%
# print(df.loc[2854740:2854746])
# datetime.fromtimestamp(1614470340), datetime.fromtimestamp(1614556740)
# (datetime.datetime(2015, 12, 31, 8, 59), datetime.datetime(2016, 1, 1, 8, 59))

# # %%
# temp_df = df.loc[1404]
# df.append(temp_df)
# # %%
# df.loc[1405]["volume"] = 0
# # %%
# df.loc[1405]
# # %%
