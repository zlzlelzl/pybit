# %%
import numpy as np
import mglearn
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from get_price_data_from_upbit import get_price_data_from_upbit

raw_data = get_price_data_from_upbit(interval="minute1", count=100)
raw_data.drop(columns=["Unnamed: 0"], inplace=True)
data = pd.DataFrame(raw_data)

data['avg20'] = data['close'].rolling(window=20).mean()
data['stddev'] = data['close'].rolling(window=20).std()
data['ubb'] = data['avg20'] + 2 * data['stddev']  # 상단밴드
data['lbb'] = data['avg20'] - 2 * data['stddev']  # 하단밴드
data['3ubb'] = data['avg20'] + 3 * data['stddev']  # 상단밴드
data['3lbb'] = data['avg20'] - 3 * data['stddev']  # 하단밴드
data['4ubb'] = data['avg20'] + 4 * data['stddev']  # 상단밴드
data['4lbb'] = data['avg20'] - 4 * data['stddev']  # 하단밴드
# %%
data["return"] = np.nan
for i in range(len(data)-1):
    if data.iloc[i+1]["close"] >= data.iloc[i]["close"]:
        print(1)
        data.iloc[i+1]["return"] = 1
    else:
        data.iloc[i+1]["return"] = 0

data
# %%

# %%
data = data[20:]
# %%
X, y = np.array(
    data[['ubb', 'lbb']]), np.array(data['close'])


data
# %%
# , '3ubb', '3lbb', '4ubb', '4lbb'
model = RandomForestClassifier(n_estimators=10, random_state=0)
model.fit(X, y)
# %%
fig, axes = plt.subplots(2, 3, figsize=(20, 10))
for i, (ax, tree) in enumerate(zip(axes.ravel(), model.estimators_)):
    ax.set_title("tree {}".format(i))
    mglearn.plots.plot_tree_partition(X, y, tree, ax=ax)

# 랜덤포레스트로 만들어진 결정경계
axes[-1, -1].set_title("Random forest")
mglearn.plots.plot_2d_separator(
    model, data, fill=True, alpha=0.5, ax=axes[-1, -1])
mglearn.discrete_scatter(X, y)

# %%
model
# %%
