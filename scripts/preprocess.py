import pandas as pd
import os

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "data", "changwon_temp.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "monthly_summary.csv")

# CSV 읽기 (EUC-KR 인코딩, 앞 7줄 건너뜀)
df = pd.read_csv(INPUT_FILE, encoding="euc-kr", skiprows=7, sep=",", engine="python")

# 컬럼명 탭·공백 제거
df.columns = df.columns.str.strip()

# 날짜 컬럼 탭 제거 (핵심!)
df["날짜"] = df["날짜"].astype(str).str.strip()

# 날짜 파싱
df["날짜"] = pd.to_datetime(df["날짜"])
df["year"] = df["날짜"].dt.year
df["month"] = df["날짜"].dt.month

# 컬럼명 확인 후 출력
print("컬럼명:", df.columns.tolist())
print("데이터 미리보기:")
print(df.head())

# 월별 집계
monthly = df.groupby(["year", "month"]).agg(
    avg_temp=("평균기온(℃)", "mean"),
    max_temp=("최고기온(℃)", "max"),
    min_temp=("최저기온(℃)", "min")
).reset_index()

# 소수점 둘째 자리 반올림
monthly = monthly.round(2)

# 저장
monthly.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n✅ 완료! {len(monthly)}개월 데이터 저장됨")
print(monthly.head())