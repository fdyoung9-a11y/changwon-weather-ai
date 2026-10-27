import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# ✅ 현재 파일 기준으로 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEY_PATH = os.path.join(BASE_DIR, "config", "firebase_key.json")
CSV_PATH = os.path.join(BASE_DIR, "data", "monthly_summary.csv")

print(f"🔑 키 경로: {KEY_PATH}")
print(f"📂 CSV 경로: {CSV_PATH}")

# Firebase 초기화
cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)

# Firestore 클라이언트
db = firestore.client()

# CSV 파일 로드
df = pd.read_csv(CSV_PATH)
print(f"📂 데이터 로드 완료: {len(df)}개 행")
print(df.head())

# Firestore에 업로드
print("\n🚀 Firestore 업로드 시작...")

for _, row in df.iterrows():
    doc_id = f"{int(row['year'])}-{int(row['month']):02d}"
    
    data = {
        "year": int(row["year"]),
        "month": int(row["month"]),
        "avg_temp": round(float(row["avg_temp"]), 1),
        "max_temp": round(float(row["max_temp"]), 1),
        "min_temp": round(float(row["min_temp"]), 1),
    }
    
    db.collection("monthly_weather").document(doc_id).set(data)
    print(f"  ✅ {doc_id} 업로드 완료")

print(f"\n🎉 총 {len(df)}개 문서 업로드 완료!")
