# %%
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import math
from datetime import datetime

# %%
# data = pd.read_csv("data_minute15_count_1000.csv")
import requests
import time
from datetime import datetime


def str_to_timestamp(s):
    return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())


end = int(time.time())
start = int(str_to_timestamp('2022-02-04 16:10:00'))

url = "https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution=1&from={start}&to={end}".format(
    start=start, end=end)
res = requests.get(url).json()

print(res)
# %%
