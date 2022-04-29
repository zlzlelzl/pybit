# pyupbit 최대 등락폭 찾기(미분)

```bash
# git에서 100mb이상 파일 등록
# https://jw910911.tistory.com/93
# https://rtyley.github.io/bfg-repo-cleaner/
git lfs install
git lfs track {filename}
# 만약 lfs하지 않고 100mb 파일을 commit했다면 오류가 남, 로그 지워야됨
# 해결법 https://rtyley.github.io/bfg-repo-cleaner/

pip install pandas
pip install matplotlib
```

## dataframe 사용법


```python
# column은 key, row는 value(list)

new_value = pd.DataFrame(data =  {'col1': [1, 2], 'col2': [3, 4]})
#      col1  col2
# 0     1     3
# 1     2     4

new_value["col1"] = [1,2]
new_value["col2"] = [3,4]
#      col1  col2
# 0     1     3
# 1     2     4
```

pyupbit의 data["close"] 데이터(종가) 사용

## 업비트 데이터를 db(csv파일)에 업데이트 하기 위해 파일 입출력
```python
    # offset을 정하기 위해 file의 크기에서 샘플 데이터의 크기를 뺌
    file_size = os.path.getsize("data.csv")

    # 데이터를 업데이트하기 위한 임시 파일 생성
    with open("data1.csv") as f1:

        # 날짜 데이터는 크기가 고정
        # 각 value들의 자릿수가 달라질 수 있으므로 (column 갯수 * column의 자릿수) 가중치        
        temp_size = len(f.readline()) + 8 * 5
        offset:int = file_size - temp_size
        # offset을 조정해주면 뒤에서부터 읽음 
        # 빠르게 연결 위치를 찾을 수 있다
        f1.seek(offset)

        # 현재 offset을 반환해주는 함수
        f1.tell()
```