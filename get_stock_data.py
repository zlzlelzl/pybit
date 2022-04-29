# %%
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import mpl_finance

start = datetime.datetime(2010, 1, 19)
end = datetime.datetime(2020, 3, 4)

data = web.DataReader("078930.KS", "yahoo", start, end)

plt.plot(data['Close'])
# %%


def get_bb(data):
    data['avg20'] = data['Close'].rolling(window=20).mean()
    data['stddev'] = data['Close'].rolling(window=20).std()
    data['ubb'] = data['avg20'] + 2 * data['stddev']  # 상단밴드
    data['lbb'] = data['avg20'] - 2 * data['stddev']  # 하단밴드
    return data


data = get_bb(data)
# %%

plt.plot(data["avg20"], color="orange")
plt.plot(data["ubb"], color="red")
plt.plot(data["lbb"], color="blue")
plt.plot(data['Close'])
# %%
# %%
