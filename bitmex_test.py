# %%
import time
import requests
from datetime import datetime
import pandas as pd


# '2022-02-04 16:10:00'
def get_price_df_from_bitmex(start, end=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')):

    def str_to_timestamp(s):
        return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())

    end = int(str_to_timestamp(end))
    start = int(str_to_timestamp(start))

    url = f"https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=60&from={start}&to={end}"
    res = requests.get(url).json()
    return res


for i in range(17, 22):
    json = get_price_df_from_bitmex(
        f'20{i}-02-22 00:00:00', f'20{i+1}-02-22 00:00:00')

    try:
        df.append(pd.DataFrame(json), ignore_index=True)
    except:
        df = pd.DataFrame(json)


# %%
df
