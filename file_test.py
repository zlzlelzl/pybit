# %%
binSize_i = 0
raw_df = bit.fetch_ohlcv(symbol="BTC/USD:BTC", limit=30,
                         timeframe=binSizes[binSize_i])
columns = ["date", "open", "high", "low", "close", "volume"]
# %%
df = pd.DataFrame(raw_df, columns=columns)
df.to_csv("ohlcv_30.csv")
# with open(f"ohlcv_30.csv", "a") as f:
#     f.writelines(raw_df)
# %%
