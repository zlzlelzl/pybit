import pandas as pd
import os
import pyupbit


def get_price_data_from_upbit(interval="minute15", count=30):
    # interval = "minute1"  # minute1
    # 1, 3, 5, 15, 10, 30, 60, 240
    # count = 100000000

    if not os.path.exists(f"data_{interval}_count_{count}.csv"):
        df = pyupbit.get_ohlcv("KRW-BTC", interval=interval, count=count)

        # 분단위로 파일 통합, 카운트를 변수로 가져갈 수 있게 수정해야됨
        df.to_csv(f"data_{interval}_count_{count}.csv")

    data = pd.read_csv(f"data_{interval}_count_{count}.csv")

    return data


if __name__ == "__main__":
    get_price_data_from_upbit(interval="minute1", count=1000)
