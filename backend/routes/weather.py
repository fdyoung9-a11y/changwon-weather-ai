from fastapi import APIRouter, HTTPException
from firebase_admin import firestore

router = APIRouter()

# 전체 데이터 조회
@router.get("/")
def get_all_weather():
    try:
        db = firestore.client()  # ✅ 함수 안으로 이동
        docs = db.collection("monthly_weather").stream()
        result = []
        for doc in docs:
            result.append(doc.to_dict())
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 연도 조회
@router.get("/{year}")
def get_weather_by_year(year: int):
    try:
        db = firestore.client()  # ✅ 함수 안으로 이동
        docs = (
            db.collection("monthly_weather")
            .where("year", "==", year)
            .stream()
        )
        result = []
        for doc in docs:
            result.append(doc.to_dict())
        if not result:
            raise HTTPException(status_code=404, detail=f"{year}년 데이터 없음")
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 연도/월 조회
@router.get("/{year}/{month}")
def get_weather_by_month(year: int, month: int):
    try:
        db = firestore.client()  # ✅ 함수 안으로 이동
        doc_id = f"{year}-{month:02d}"
        doc = db.collection("monthly_weather").document(doc_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"{year}년 {month}월 데이터 없음")
        return {"data": doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))