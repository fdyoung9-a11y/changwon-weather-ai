from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ─────────────────────────────────────────
# 📦 요청 데이터 모델
# ─────────────────────────────────────────
class WeatherData(BaseModel):
    year: int
    month: int
    avg_temp: float
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    rainfall: Optional[float] = None

class WeatherUpdateData(BaseModel):
    avg_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    rainfall: Optional[float] = None


# ─────────────────────────────────────────
# 📖 GET - 전체 데이터 조회
# ─────────────────────────────────────────
@router.get("/")
def get_all_weather():
    try:
        db = firestore.client()
        docs = db.collection("monthly_weather").stream()
        result = [doc.to_dict() for doc in docs]
        return {"count": len(result), "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 📖 GET - 특정 연도 조회
# ─────────────────────────────────────────
@router.get("/{year}")
def get_weather_by_year(year: int):
    try:
        db = firestore.client()
        docs = (
            db.collection("monthly_weather")
            .where("year", "==", year)
            .stream()
        )
        result = [doc.to_dict() for doc in docs]
        if not result:
            raise HTTPException(status_code=404, detail=f"{year}년 데이터 없음")
        return {"count": len(result), "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 📖 GET - 특정 연도/월 조회
# ─────────────────────────────────────────
@router.get("/{year}/{month}")
def get_weather_by_month(year: int, month: int):
    try:
        db = firestore.client()
        doc_id = f"{year}-{month:02d}"
        doc = db.collection("monthly_weather").document(doc_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"{year}년 {month}월 데이터 없음")
        return {"data": doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# ✏️ POST - 새 데이터 추가
# ─────────────────────────────────────────
@router.post("/")
def create_weather(data: WeatherData):
    try:
        db = firestore.client()
        doc_id = f"{data.year}-{data.month:02d}"

        # 중복 확인
        doc = db.collection("monthly_weather").document(doc_id).get()
        if doc.exists:
            raise HTTPException(
                status_code=409,
                detail=f"{data.year}년 {data.month}월 데이터가 이미 존재합니다"
            )

        # 저장
        db.collection("monthly_weather").document(doc_id).set(data.dict())
        return {"message": "데이터 추가 완료", "id": doc_id, "data": data.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 🔄 PUT - 데이터 수정
# ─────────────────────────────────────────
@router.put("/{year}/{month}")
def update_weather(year: int, month: int, data: WeatherUpdateData):
    try:
        db = firestore.client()
        doc_id = f"{year}-{month:02d}"

        # 존재 확인
        doc = db.collection("monthly_weather").document(doc_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"{year}년 {month}월 데이터 없음")

        # None 제외하고 수정된 값만 업데이트
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다")

        db.collection("monthly_weather").document(doc_id).update(update_data)
        return {"message": "데이터 수정 완료", "id": doc_id, "updated": update_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 🗑️ DELETE - 데이터 삭제
# ─────────────────────────────────────────
@router.delete("/{year}/{month}")
def delete_weather(year: int, month: int):
    try:
        db = firestore.client()
        doc_id = f"{year}-{month:02d}"

        # 존재 확인
        doc = db.collection("monthly_weather").document(doc_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"{year}년 {month}월 데이터 없음")

        db.collection("monthly_weather").document(doc_id).delete()
        return {"message": "데이터 삭제 완료", "id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))