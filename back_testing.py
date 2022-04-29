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
from itertools import combinations

base_url = "https://www.bitmex.com/api/v1"
test_base_url = "https://testnet.bitmex.com/api/v1"

# test_api_key = ""
# test_api_secret = ""
# api_key = ""
# api_secret = ""

path = "/trade/bucketed"  # "/history"
headers = {"Accept": "application/json"}

# raw_df = get_price_data_from_upbit(interval="minute1", count=10000)

# '2017-01-01 00:00:00', '2018-01-01 00:00:00'


def get_price_df_from_bitmex(start, end=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')):

    def str_to_timestamp(s):
        return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())

    end = int(str_to_timestamp(end))
    start = int(str_to_timestamp(start))

    url = f"https://www.bitmex.com/api/udf/history?symbol=XBTUSD&resolution={1}&from={start}&to={end}"
    res = requests.get(url).json()
    return res


raw_df = pd.read_csv(f"data_bitmex_minute1.csv").drop(
    "Unnamed: 0", axis="columns")

# 시간대 설정

raw_df = raw_df[3257403:]
# raw_df

# df[df['s'].isnull()]
# datetime.datetime(2022, 2, 5, 0, 0) # 까지 데이터
# datetime.fromtimestamp(raw_df.loc[1]["date"])
# %%
# ticker 변화


def set_minutes_ticker(temp_df, minutes):

    def get_first(arr):
        return arr.iloc[0]

    def get_last(arr):
        return arr.iloc[-1]

    conditions = temp_df['date']//(minutes * 60)
    return temp_df.groupby(conditions).agg(
        {"date": get_first,
         "open": get_first, "high": max,
         "low": min, "close": get_last,
         "volume": sum}).reset_index(drop=True)


mov_avgs = (5, 20, 60, 120, 200)
combinations_mov_avgs = list(combinations(mov_avgs, 2))
hh = 60
dd = hh*24
# for time_case in [dd*30]:
for time_case in [1, 2, 3, 5, 15, 30, hh, hh*6, hh*12, dd, dd*2, dd*3, dd*7, dd*30]:
    df = set_minutes_ticker(raw_df, time_case)

    binSizes = ["1m"]
    for binSize_i in range(len(binSizes)):

        temp_count = 1
        max_ubb_sum, max_lbb_sum, max_bb_sum = 0, 0, 0

        if 1:
            bought_upper_ubb = [[] for _ in range(len(binSizes))]
            bought_upper_date = [[] for _ in range(len(binSizes))]
            sold_upper_ubb = [[] for _ in range(len(binSizes))]
            sold_upper_date = [[] for _ in range(len(binSizes))]
            bought_lower_ubb = [[] for _ in range(len(binSizes))]
            bought_lower_date = [[] for _ in range(len(binSizes))]
            sold_lower_ubb = [[] for _ in range(len(binSizes))]
            sold_lower_date = [[] for _ in range(len(binSizes))]

            is_bought_upper_ubb = [0] * len(binSizes)
            is_bought_lower_lbb = [0] * len(binSizes)
            is_bought_regression_ubb = False
            is_bought_regression_lbb = False
            upper_ubb_length = [0] * len(binSizes)
            lower_lbb_length = [0] * len(binSizes)
            ubb_sum = 0
            lbb_sum = 0
            max_is_bought_upper_ubb = [0] * len(binSizes)
            max_is_bought_lower_lbb = [0] * len(binSizes)
            maintain_indices_upper = [0] * len(binSizes)
            maintain_indices_lower = [0] * len(binSizes)
            is_bought_upper_4ubb = [0] * len(binSizes)
            is_bought_lower_4lbb = [0] * len(binSizes)
            count_upper_4ubb = [0] * len(binSizes)
            count_lower_4lbb = [0] * len(binSizes)
            count_bought_upper_ubb = [0] * len(binSizes)
            count_bought_lower_lbb = [0] * len(binSizes)
            ubb_end_idx = []
            lbb_end_idx = []
            ubb_end_idx_minus = []
            lbb_end_idx_minus = []
            # []부분 binSize에 최적화 필요
            ubb_dx = []
            lbb_dx = []

            # 추세매매를 위한 이평선

            for ma in mov_avgs:
                df[f'avg{ma}'] = df['close'].rolling(window=ma).mean()
            df['stddev'] = df['close'].rolling(window=20).std()
            df['ubb'] = df['avg20'] + 2 * df['stddev']  # 상단밴드
            df['lbb'] = df['avg20'] - 2 * df['stddev']  # 하단밴드
            df['3ubb'] = df['avg20'] + 3 * df['stddev']  # 상단밴드
            df['3lbb'] = df['avg20'] - 3 * df['stddev']  # 하단밴드
            df['4ubb'] = df['avg20'] + 4 * df['stddev']  # 상단밴드
            df['4lbb'] = df['avg20'] - 4 * df['stddev']  # 하단밴드

            # 시나리오 (단타 확인 안되면 다 버림)
            # 1. ubb보다 높을때 담고 ubb안으로 들어오면 판다. ubb 유지인덱스마다 확인
            # 2. ubb보다 높을때 담고 ubb안으로 들어와서 다시 양전하면 판다. ubb 유지인덱스마다 확인
            # 3. ubb보다 높을때 계속 담고 20이평선에 닿았을때 다 판다.
            # 4. ubb보다 높을때 담고 20이평선에 닿거나 틱 몇개 이상 지나면 판다. ubb 유지인덱스마다 확인, 틱마다 확인하여 최대값 찾기
            # 6. ubb보다 높을때 담고 ubb안으로 들어오면 판다. ubb 유지인덱스마다 확인. 청산 나오는 횟수 확인(최대 유지인덱스)
            # 7. ubb보다 높을때 고배율 ubb안으로 들어오면 판다. ubb 유지인덱스마다 확인. 청산 나오는 횟수 확인(최대 유지인덱스)
            # 8. 100배 1분봉으로 터진 방향으로 250
            # 9. 변동성 돌파 전략
            bat_val = (df["high"][0] + df["low"][0]) / 2

            upside = []
            downside = []

            taker_fee = -0.0001
            maker_fee = 0.0005
            K = 0.5
            last_range = 99999999
            upper_order = 0
            lower_order = 0
            upper_sum = 0
            lower_sum = 0
            last_low = 0
            last_high = 0
            last_close = 0

            upper_order_price = [0 for _ in range(201)]
            upper_profit = [0 for _ in range(201)]
            upper_profits = [[] for _ in range(201)]
            upper_profit_rates = [[] for _ in range(201)]
            upper_order_count = [0 for _ in range(201)]
            lower_order_price = [0 for _ in range(201)]
            lower_profit = [0 for _ in range(201)]
            lower_profits = [[] for _ in range(201)]
            lower_profit_rates = [[] for _ in range(201)]

            lower_list = []
            last_upper_order = 0
            last_lower_order = 0
            nan = df["avg5"][0]
            fee = maker_fee

            # 1분봉, 20, 60평선, 캔들 정렬
            #

            last_high, last_low = df["open"][0], df["close"][0]
            last_open, last_close = df["open"][0], df["close"][0]
            last_range = df["high"][0] - df["low"][0]

            # buy_order_trends = [[] for _ in range(201)]
            buy_order_trends = dict()
            for com_ma in combinations_mov_avgs:

                sell_order_trends = [[] for _ in range(201)]

            # 빅웨이브까지 거리 계산해보기, 빅웨이브

            for i in range(1, len(df)):
                # 일반 추세 추종
                # 이동평균선을 상승돌파하면 매수하고 하락이탈하면 매도

                # for ma in mov_avgs:
                for com_ma in combinations_mov_avgs:
                    # if not pd.isnull(df[f"avg{ma}"][i]):
                    # 이평선 조합
                    if not buy_order_trends[ma]:
                        if df["close"][i] >= df[f"avg{com_ma[-1]}"][i]:
                            for com_ma_avgs in com_ma[:-1]:
                                if df["close"][i] < df[f"avg{com_ma_avgs}"][i]:
                                    break

                            buy_order_trends[ma] = "buy"
                            # 마감 가격
                            # upper_order_price[ma] = df["close"][i]
                            # 이평선 가격
                            upper_order_price[ma] += df[f"avg{ma}"][i]
                            upper_order_count[ma] += 1

                    elif buy_order_trends[ma]:
                        if df["close"][i] >= df[f"avg{com_ma[-1]}"][i]:
                            # for com_ma in combinations_mov_avgs[0]:
                            #     if df["close"][i] < df[f"avg{com_ma}"][i]:
                            #         break
                            if df["close"][i] >= df[f"avg{combinations_mov_avgs[0]}"][i]:
                                upper_order_price[ma] += df[f"avg{combinations_mov_avgs[0]}"][i]
                                upper_order_count[ma] += 1

                        else:
                            buy_order_trends[ma] = ""
                            upper_profit[ma] = - \
                                (upper_order_price[ma] * (1+fee)) + \
                                (df["close"][i] * (1-fee)
                                 * upper_order_count)
                            upper_order_count = 0
                            upper_profits[ma].append(
                                upper_profit[ma]
                            )
                            upper_profit_rates[ma].append(
                                (upper_profit[ma] /
                                    (upper_order_price[ma] * (1+fee))) * 100
                            )

                            # 구매 추세, 이평선 돌파
                            # if not buy_order_trends[ma] and df["close"][i] >= df[f"avg{ma}"][i]:
                            #     buy_order_trends[ma] = "buy"
                            #     # 마감 가격
                            #     # upper_order_price[ma] = df["close"][i]
                            #     # 이평선 가격
                            #     upper_order_price[ma] = df[f"avg{ma}"][i]

                            # if buy_order_trends[ma] and df["close"][i] <= df[f"avg{ma}"][i]:
                            #     buy_order_trends[ma] = ""
                            #     upper_profit[ma] = - \
                            #         (upper_order_price[ma] * (1+fee)) + \
                            #         (df["close"][i] * (1-fee))
                            #     upper_profits[ma].append(
                            #         upper_profit[ma]
                            #     )
                            #     upper_profit_rates[ma].append(
                            #         (upper_profit[ma] /
                            #          (upper_order_price[ma] * (1+fee))) * 100
                            #     )

                            # # 판매 추세, 이평선 돌파
                            # if not sell_order_trends[ma] and df["close"][i] <= df[f"avg{ma}"][i]:
                            #     sell_order_trends[ma] = "sell"
                            #     # lower_order_price[ma] = df["close"][i]
                            #     lower_order_price[ma] = df[f"avg{ma}"][i]

                            # if sell_order_trends[ma] and df["close"][i] >= df[f"avg{ma}"][i]:
                            #     sell_order_trends[ma] = ""
                            #     lower_profit[ma] = (
                            #         lower_order_price[ma] * (1-fee)) - \
                            #         (df["close"][i] * (1+fee))
                            #     lower_profits[ma].append(
                            #         lower_profit[ma]
                            #     )

                            #     lower_profit_rates[ma].append(
                            #         (lower_profit[ma] /
                            #          (lower_order_price[ma] * (1+fee))) * 100
                            #     )

            print_upper_profits = ""
            print_upper_profit_rates = ""
            print_lower_profits = ""
            print_lower_profit_rates = ""
            for ma in mov_avgs:
                print_upper_profits += f"upper_list{ma} : {int(sum(upper_profits[ma]))} "
                print_upper_profit_rates += f"upper_rate{ma} : {sum(upper_profits[ma])//len(upper_profits[ma]) if len(upper_profits[ma]) != 0 else 0} "
                print_lower_profits += f"lower_list{ma} : {int(sum(lower_profits[ma]))} "
                print_lower_profit_rates += f"lower_rate{ma} : {sum(lower_profits[ma])//len(lower_profits[ma]) if len(lower_profits[ma]) != 0 else 0} "
            print(
                (time_case//60, '시간') if time_case//60 % 24 != 0 else (time_case//60//24, '일'), "봉", print_upper_profits)
            print((time_case//60, '시간') if time_case//60 % 24 != 0 else (time_case//60//24, '일'), "봉",
                  print_upper_profit_rates)
            print()
            print(
                (time_case//60, '시간') if time_case//60 % 24 != 0 else (time_case//60//24, '일'), "봉", print_lower_profits)
            print((time_case//60, '시간') if time_case//60 % 24 != 0 else (time_case//60//24, '일'), "봉",
                  print_lower_profit_rates)
            print()
            print()
            # print(upper_profit_rates
            # 커스텀 추세 추종 전략
            # 추세가 유지되면 가만히 두고, 추세가 바뀌면 손절하고 다시 산다

            # 롱 추세
            # if trend == "buy":
            #     # 추세 유지
            #     if df["close"][i] >= last_close:
            #         upper_sum += df["close"][i] - last_close
            #         last_upper_order = df["close"][i]

            #     # 추세 전환 재구매
            #     else:
            #         upper_sum += df["close"][i] - last_close

            # last_high, last_low = df["high"][i], df["low"][i]
            # last_open, last_close = df["open"][i], df["close"][i]
            # last_range = df["high"][i] - df["low"][i]

            # # 변동성 지표 전략 -> 1~2월 전 시간대로는 안맞음
            # try:
            #     noise = 1 - abs(last_open-last_close)/(last_high-last_low)
            #     K = noise**2
            # except:
            #     K = 0.5
            # upper_break_price = last_range * K + df["open"][i]
            # if upper_break_price < df["high"][i]:
            #     # upper_order = upper_break_price # 주문
            #     # print(i, "롱산다", upper_break_price, df["close"][i])
            #     upper_list.append(
            #         -(upper_break_price * (1+fee)) +
            #         (df["close"][i] * (1-fee)))
            # else:
            #     pass

            # lower_break_price = df["open"][i] - last_range * K
            # if lower_break_price > df["low"][i]:
            #     # upper_order = upper_break_price # 주문
            #     # print(i, "숏산다", lower_break_price, df["close"][i])
            #     lower_list.append(
            #         (lower_break_price * (1-fee)) -
            #         (df["close"][i] * (1+fee)))
            # else:
            #     pass

            # print(sum(upper_list), sum(lower_list))
            # print(i, upper_sum, lower_sum)

            #       upper_break_price < df["high"][i],
            #       now_upper_order, upper_sum)

            # lower_break_price = df["open"][i] - last_range * K
            # if lower_break_price > df["low"][i]:  # 산다
            #     if now_lower_order == 0:  # 중복구매 방지
            #         now_lower_order = lower_break_price
            # else:  # 안산다
            #     if now_lower_order != 0:  # 중복 초기화
            #         lower_sum += now_lower_order - lower_break_price
            #         now_lower_order = 0
            # last_high, last_low = df["high"][i], df["low"][i]
            # last_open, last_close = df["open"][i], df["close"][i]
            # last_range = df["high"][i] - df["low"][i]

            # print(i, upper_sum, lower_sum)

            # maintain_indices_upper[binSize_i] = maintain_indices_lower[binSize_i] = 1

            # 자리 바꿔보면서 다른지 확인 -> up, down 중복되는 i 찾아봐야됨
            # 있으면 그때가서 해결법 찾기
            # 예상해결법) 추세를 찾는거니까 bat_val에서 low, high 먼쪽으로 몰아주기

            # if df["high"][i] >= bat_val + temp_weight:
            #     while df["high"][i] >= bat_val + temp_weight:
            #         upside.append(i)
            #         bat_val += temp_weight

            # # print(bat_val)

            # if df["low"][i] <= bat_val + temp_weight:
            #     while df["low"][i] <= bat_val + temp_weight:
            #         downside.append(i)
            #         bat_val -= temp_weight

            # 약 200만개의 데이터, 2266796
            # 인덱스 찾아야됨

            # 4시그마에 사서 2시그마에 파는전략
            # 종가에 사서 종가에 팔면 승률 66.4%, 70.5%. 이익 1862000, 441000
            # 시초가에 사서 시초가에 팔면 93.2%, 94.2%. 이익 81275884, -81030536
            # if not is_bought_upper_4ubb[binSize_i] and df["high"][i] > df["4ubb"][i]:
            #     fee = df["4ubb"][i] * 0.075
            #     ubb_sum += df["4ubb"][i] - fee
            #     count_upper_4ubb[binSize_i] += 1
            #     # print("ubb_sum", ubb_sum)
            #     is_bought_upper_4ubb[binSize_i] = 1

            # elif is_bought_upper_4ubb[binSize_i]:
            #     count_bought_upper_ubb[binSize_i] += 1
            #     if df["low"][i] < df["ubb"][i] or count_bought_upper_ubb[binSize_i] > temp_count:
            #         count_bought_upper_ubb[binSize_i] = 1
            #         fee = df["ubb"][i] * 0.075
            #         ubb_sum -= df["ubb"][i] - fee
            #         ubb_dx.append(ubb_sum)
            #         is_bought_upper_4ubb[binSize_i] = 0

            # if not is_bought_lower_4lbb[binSize_i] and df["low"][i] < df["4lbb"][i]:
            #     fee = df["4lbb"][i] * 0.075
            #     lbb_sum += df["4lbb"][i] - fee
            #     count_lower_4lbb[binSize_i] += 1
            #     # print("lbb_sum", ubb_sum)
            #     is_bought_lower_4lbb[binSize_i] = 1

            # elif is_bought_lower_4lbb[binSize_i]:
            #     count_bought_lower_lbb[binSize_i] += 1
            #     if df["high"][i] > df["lbb"][i] or count_bought_lower_lbb[binSize_i] > temp_count:
            #         count_bought_lower_lbb[binSize_i] = 1
            #         fee = df["lbb"][i] * 0.075
            #         lbb_sum -= df["lbb"][i] - fee
            #         lbb_dx.append(lbb_sum)
            #         is_bought_lower_4lbb[binSize_i] = 0

            # # 4bb 구매 후 위 아래로 걸어놓기
            # if not is_bought_upper_4ubb[binSize_i] and df["high"][i] > df["4ubb"][i]:
            #     fee = df["4ubb"][i] * 0.025
            #     ubb_sum += df["4ubb"][i] - fee
            #     count_upper_4ubb[binSize_i] += 1
            #     purchased_price_high = df["4ubb"][i]
            #     is_bought_upper_4ubb[binSize_i] = 1

            # # 손실을 우선으로 해서 최소한을 보장
            # # 손실
            # if is_bought_upper_4ubb[binSize_i] and df["high"][i] > purchased_price_high + temp_val:
            #     fee = (purchased_price_high + temp_val) * 0.025
            #     ubb_sum -= purchased_price_high - temp_val - fee
            #     ubb_dx.append(ubb_sum)
            #     is_bought_upper_4ubb[binSize_i] = 0
            # # 이득
            # elif is_bought_upper_4ubb[binSize_i] and df["low"][i] < purchased_price_high - temp_val:
            #     fee = (purchased_price_high - temp_val) * 0.025
            #     ubb_sum -= purchased_price_high + temp_val - fee
            #     ubb_dx.append(ubb_sum)
            #     is_bought_upper_4ubb[binSize_i] = 0

            # # 4bb 구매 후 위 아래로 걸어놓기
            # if not is_bought_lower_4lbb[binSize_i] and df["low"][i] < df["4lbb"][i]:
            #     fee = df["4lbb"][i] * 0.025
            #     lbb_sum += df["4lbb"][i] - fee
            #     count_lower_4lbb[binSize_i] += 1
            #     purchased_price_low = df["4lbb"][i]
            #     is_bought_lower_4lbb[binSize_i] = 1

            # # 손실을 우선으로 해서 최소한을 보장
            # # 손실
            # if is_bought_lower_4lbb[binSize_i] and df["low"][i] < purchased_price_low - temp_val:
            #     fee = (purchased_price_low - temp_val) * 0.025
            #     lbb_sum -= purchased_price_low + temp_val - fee
            #     lbb_dx.append(lbb_sum)
            #     is_bought_lower_4lbb[binSize_i] = 0

            # # 이득
            # elif is_bought_lower_4lbb[binSize_i] and df["high"][i] > purchased_price_low + temp_val:
            #     fee = (purchased_price_low + temp_val) * 0.025
            #     lbb_sum -= purchased_price_low - temp_val - fee
            #     lbb_dx.append(lbb_sum)
            #     is_bought_lower_4lbb[binSize_i] = 0

            # print(downside, upside)

            # for i in range(1, len(ubb_dx)):
            #     ubb_dx[i-1] = ubb_dx[i] - ubb_dx[i-1]

            # for i in range(1, len(lbb_dx)):
            #     lbb_dx[i-1] = lbb_dx[i] - lbb_dx[i-1]

            # ubb_win_num, ubb_lose_num = len(list(filter(lambda x: x >= 0, ubb_dx))), len(
            #     list(filter(lambda x: x < 0, ubb_dx)))
            # lbb_lose_num, lbb_win_num = len(list(filter(lambda x: x >= 0, lbb_dx))), len(
            #     list(filter(lambda x: x < 0, lbb_dx)))
            # print(len(list(filter(lambda x: x >= 0, ubb_dx))),
            #       len(list(filter(lambda x: x < 0, ubb_dx))))
            # print(len(list(filter(lambda x: x >= 0, lbb_dx))),
            #       len(list(filter(lambda x: x < 0, lbb_dx))))
            # print(temp_val, ubb_win_num, ubb_lose_num, lbb_win_num, lbb_lose_num)

            # print(f"{round(ubb_win_num/(ubb_win_num+ubb_lose_num)*100,1)}%, {round(lbb_win_num/(lbb_win_num+lbb_lose_num)*100,1)}%. 이익 {int(ubb_sum)}, {int(lbb_sum)}")
            # if max_ubb_sum < ubb_sum:
            #     max_ubb_sum = ubb_sum
            #     max_ubb_sum_val = temp_val
            # if max_lbb_sum > lbb_sum:
            #     max_lbb_sum = lbb_sum
            #     max_lbb_sum_val = temp_val
            # if max_bb_sum < ubb_sum - lbb_sum:
            #     max_bb_sum = ubb_sum - lbb_sum
            #     max_bb_sum_val = temp_val
        # # 1. ubb보다 높을때 담고 ubb안으로 들어오면 판다. ubb 유지인덱스마다 확인
        # if df["close"][i] > df["ubb"][i]:
        #     is_bought_upper_ubb[binSize_i] += 1
        #     if is_bought_upper_ubb[binSize_i] > maintain_indices_upper[binSize_i]:
        #         ubb_sum += df["close"][i]

        # elif is_bought_upper_ubb[binSize_i] > maintain_indices_upper[binSize_i] and df["close"][i] < df["ubb"][i]:
        #     ubb_sum -= df["close"][i] * \
        #         (is_bought_upper_ubb[binSize_i] -
        #          maintain_indices_upper[binSize_i])
        #     print("upper", is_bought_upper_ubb[binSize_i], i, ubb_sum)
        #     max_is_bought_upper_ubb[binSize_i] = max(
        #         max_is_bought_upper_ubb[binSize_i], is_bought_upper_ubb[binSize_i])
        #     is_bought_upper_ubb[binSize_i] = 0

        # if df["close"][i] < df["lbb"][i]:
        #     is_bought_lower_lbb[binSize_i] += 1
        #     if is_bought_lower_lbb[binSize_i] > maintain_indices_lower[binSize_i]:
        #         lbb_sum += df["close"][i]

        # elif is_bought_lower_lbb[binSize_i] > maintain_indices_upper[binSize_i] and df["close"][i] > df["lbb"][i]:
        #     lbb_sum -= df["close"][i] * \
        #         (is_bought_lower_lbb[binSize_i] -
        #          maintain_indices_lower[binSize_i])
        #     # print("lower", is_bought_lower_lbb[binSize_i], i, lbb_sum)
        #     max_is_bought_lower_lbb[binSize_i] = max(
        #         max_is_bought_lower_lbb[binSize_i], is_bought_lower_lbb[binSize_i])
        #     is_bought_lower_lbb[binSize_i] = 0

        # # 종가가 ubb보다 높을때 담는다
        # if df["close"][i] > ubb[i]:
        #     bought_upper_ubb[binSize_i].append(ubb[i])
        #     bought_upper_date[binSize_i].append(df["date"][i])
        #     is_bought_upper_ubb[binSize_i] += 1

        # # 볼린저 입성할때 팖
        # if df["close"][i] < ubb[i]:
        #     sold_upper_ubb[binSize_i].append(df["close"][i])
        #     sold_upper_date[binSize_i].append(df["date"][i])
        #     is_bought_upper_ubb[binSize_i] = 0
        #     # upper_ubb_length[binSize_i] =

        # # 볼린저 밴드 탈출 추격숏
        # if not is_bought_lower_lbb[binSize_i] and df["low"][i] < lbb[i]:
        #     bought_lower_ubb[binSize_i].append(ubb[i])
        #     bought_lower_date[binSize_i].append(df["date"][i])

        # # 양전하거나 볼린저 입성할때 팖
        # if is_bought_lower_lbb[binSize_i] and (df["close"][i] > df["open"][i] or df["close"][i] > lbb[i]):
        #     sold_lower_ubb[binSize_i].append(df["close"][i])
        #     sold_lower_date[binSize_i].append(df["date"][i])

        # plt.plot(df["date"].index, df["avg5"], color="green", label="5")
        # # plt.plot(df["date"].index, df["avg10"], color="orange", label="10")
        # plt.plot(df["date"].index, df["avg60"], color="orange", label="60")
        # plt.plot(df["date"].index, df["avg120"], color="purple", label="120")
        # plt.plot(df["date"].index, df["avg200"], color="yellow", label="200")

        # plt.plot(df["date"].index, df["avg20"], color="red")
        # plt.plot(df["date"].index, df["ubb"], color="red")
        # plt.plot(df["date"].index, df["lbb"], color="blue")
        # plt.plot(df["date"].index, df["4ubb"], color="purple")
        # plt.plot(df["date"].index, df["4lbb"], color="navy")

        # mpl_finance.candlestick2_ohlc(ax, opens=df['open'], highs=df['high'],
        #                             lows=df['low'], closes=df['close'], width=0.5, colorup='r', colordown='b')
        # 마지막 dx는 청산이 안되어있을수도 있으므로
        # print(ubb_sum)
        #   , lbb_sum - lbb_dx[-1])
        # plt.legend()
        # plt.show()
send_message("1")
# %%

# 안 팔고 들고있는거는 계산x
bought_upper_ubb = bought_upper_ubb[:len(sold_upper_ubb)]
bought_lower_ubb = bought_lower_ubb[:len(sold_lower_ubb)]
# %%
# 롱 포지션
# np.array(sold_upper_ubb) - np.array(bought_upper_ubb)
# %%
# 숏 포지션
# np.array(bought_lower_ubb) - np.array(sold_lower_ubb)
# %%
# (1비트, x1 레버리지 투자시)
# 롱 총 수익
sum(sold_upper_ubb) - sum(bought_upper_ubb)
# %%
# 숏 총 수익
sum(bought_lower_ubb) - sum(sold_lower_ubb)
# %%
# 롱 승률
profit_day = 0
for i in range(len(sold_upper_ubb)):
    if sold_upper_ubb[i] - bought_upper_ubb[i] >= 0:
        profit_day += 1

print(profit_day / len(sold_upper_ubb) * 100)
# %%
# 숏 승률
profit_day = 0
for i in range(len(bought_lower_ubb)):
    if bought_lower_ubb[i] - sold_lower_ubb[i] >= 0:
        profit_day += 1

print(profit_day / len(sold_lower_ubb) * 100)

# %%

# %%
ubb_sum
# %%
lbb_sum
# %%
max_is_bought_upper_ubb[0]
# %%
max_is_bought_lower_lbb[0]

# %%
for i in range(1, len(ubb_dx)):
    ubb_dx[i-1] = ubb_dx[i] - ubb_dx[i-1]
for i in range(1, len(lbb_dx)):
    lbb_dx[i-1] = lbb_dx[i] - lbb_dx[i-1]

print(len(list(filter(lambda x: x >= 0, ubb_dx))),
      len(list(filter(lambda x: x < 0, ubb_dx))))
print(len(list(filter(lambda x: x >= 0, lbb_dx))),
      len(list(filter(lambda x: x < 0, lbb_dx))))

# %%
print(ubb_dx)
# %%
print(max_ubb_sum_val, max_lbb_sum_val, max_bb_sum_val)

# %%
new_df = pd.DataFrame(df[:0])
new_df
# %%
new_df["bat"] = 0

# %%
new_df
# %%
now_4ubb = df["4ubb"][29]
now_ubb = df["ubb"][29]

now_4ubb, now_ubb
# %%
datetime.fromtimestamp(1593185820)
# %%
# %%


def str_to_timestamp(s):
    return time.mktime(datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())


str_to_timestamp('2022-1-24 00:00:00')


raw_df.query(f"date==1638630000").index[0]

# s_idx = raw_df.query(f"date==1443184440").index[0]
# ["date"][1443184440]

# %%
len(raw_df)
# %%
raw_df
# %%
combinations_mov_avgs = list(combinations(mov_avgs, 2))
for com_ma in combinations_mov_avgs:
    print("".join(com_ma))
