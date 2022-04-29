# %%
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 정규화 함수


def MinMaxScaler(data):
    denom = np.max(data, 0)-np.min(data, 0)
    nume = data-np.min(data, 0)
    return nume/denom

# 정규화 되돌리기 함수


def back_MinMax(data, value):
    diff = np.max(data, 0)-np.min(data, 0)
    back = value * diff + np.min(data, 0)
    return back


# 데이터 불러오기
_xy = np.loadtxt("data-02-stock_daily.csv", delimiter=",", skiprows=0+1+1)
# xy = xy[::-1]

# %%
# plt.plot(xy[:, 4])  # 전체 종가
# %%
_xy
# %%
