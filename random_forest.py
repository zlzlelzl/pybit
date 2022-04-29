# %%
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from get_price_data_from_upbit import get_price_data_from_upbit

sam = get_price_data_from_upbit(interval="minute1", count=1000)

sam = sam.sort_index(ascending=False)
sam = sam.reset_index()
sam = sam.drop(["index"], axis=1)
sam.rename(columns={"close": "Close"}, inplace=True)
sam["return"] = np.nan  # 나중에 값을 채울 Column을 미리 Nan값으로 생성

data = sam[["Close", "return"]]
data = pd.DataFrame(data)

for i in range(len(data)-1):
    if (data.iloc[i+1]["Close"]/data.iloc[i]["Close"])-1 >= 0:
        data.iloc[i+1]["return"] = 1

    else:
        data.iloc[i+1]["return"] = 0


data['avg20'] = data['Close'].rolling(window=20).mean()
data['stddev'] = data['Close'].rolling(window=20).std()
data['ubb'] = data['avg20'] + 2 * data['stddev']  # 상단밴드
data['lbb'] = data['avg20'] - 2 * data['stddev']  # 하단밴드
data['3ubb'] = data['avg20'] + 3 * data['stddev']  # 상단밴드
data['3lbb'] = data['avg20'] - 3 * data['stddev']  # 하단밴드
data['4ubb'] = data['avg20'] + 4 * data['stddev']  # 상단밴드
data['4lbb'] = data['avg20'] - 4 * data['stddev']  # 하단밴드

data = data[20:]

feature_list = []
label_list = []

for i in range(len(data)-20):
    feature_list.append(np.array(data.iloc[0:20]["ubb"]))
    label_list.append(np.array(data.iloc[i+20]["return"]))

data_X = np.array(feature_list)
data_Y = np.array(label_list)

train_data, train_label = data_X[:-30], data_Y[:-30]
test_data, test_label = data_X[-30:], data_Y[-30:]

train_data = pd.DataFrame(train_data)
train_label = pd.DataFrame(train_label)
test_data = pd.DataFrame(test_data)
test_label = pd.DataFrame(test_label)


# base model
forest = RandomForestClassifier(n_estimators=10)
forest.fit(train_data, train_label.values.ravel())

y_pred = forest.predict(test_data)
print("accuracy: {}".format(metrics.accuracy_score(y_pred, test_label)))
# %%
