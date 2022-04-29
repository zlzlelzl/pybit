# %%
def get_data(interval="minute1"):
    import pyupbit
    import os
    import sys

    df = pyupbit.get_ohlcv("KRW-BTC", interval=interval, count=100)

    if not os.path.isfile(f"data_{interval}.csv"):
        df.to_csv(f"data_{interval}.csv")
        print("make file")
        return True

    file_size = os.path.getsize(f"data_{interval}.csv")

    with open(f"data_{interval}.csv", "r") as f:
        f.readline()  # column의 크기는 필요없으므로

        # 5행을 뺀 데이터를 업데이트한다
        # 각 value들의 자릿수가 달라질 수 있으므로 (column 갯수 * column의 자릿수) 가중치
        temp_size = len(f.readline()) + 8 * 5
        offset = file_size - temp_size

        f.seek(offset)

        data = f.readlines()
        print(data)
        with open(f"data_{interval}.csv") as f1:
            f1.readline()  # column명 지우기
            while data[-1][:20] != f1.readline()[:20]:
                pass

            add_data = f1.readlines()

    with open(f"data_{interval}.csv", "a") as f:
        f.writelines(add_data)


if __name__ == "__main__":
    get_data(interval="minute1")

# %%
