from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta

# 한국 시간대(UTC보다 9시간 빠름)
KST = timezone(timedelta(hours=9))

router = APIRouter()

# ─────────────────────────────────────────
# 📦 요청 데이터 모델
# ─────────────────────────────────────────
class ConversationCreate(BaseModel):
    user_message: str        # 사용자 질문
    bot_response: str        # AI 답변
    session_id: Optional[str] = None  # 대화 세션 구분용 (선택)


# ─────────────────────────────────────────
# 📖 GET - 전체 대화 목록 조회
# ─────────────────────────────────────────
@router.get("/")
def get_all_conversations():
    try:
        db = firestore.client()
        docs = (
            db.collection("conversations")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .stream()
        )
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id   # 문서 ID도 함께 반환
            result.append(data)
        return {"count": len(result), "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 📖 GET - 특정 대화 조회
# ─────────────────────────────────────────
@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    try:
        db = firestore.client()
        doc = db.collection("conversations").document(conversation_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="대화 기록을 찾을 수 없습니다")
        data = doc.to_dict()
        data["id"] = doc.id
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 📖 GET - 세션별 대화 조회
# ─────────────────────────────────────────
@router.get("/session/{session_id}")
def get_conversations_by_session(session_id: str):
    try:
        db = firestore.client()
        docs = (
            db.collection("conversations")
            .where("session_id", "==", session_id)
            .order_by("created_at", direction=firestore.Query.ASCENDING)
            .stream()
        )
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)
        if not result:
            raise HTTPException(status_code=404, detail=f"세션 {session_id} 대화 없음")
        return {"count": len(result), "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# ✏️ POST - 대화 저장
# ─────────────────────────────────────────
@router.post("/")
def create_conversation(data: ConversationCreate):
    try:
        db = firestore.client()

        # 저장할 데이터 구성
        save_data = {
            "user_message": data.user_message,
            "bot_response": data.bot_response,
            "session_id": data.session_id,
            "created_at": datetime.now(KST).isoformat()  # 시간 자동 기록
        }

        # Firestore 자동 ID로 저장
        doc_ref = db.collection("conversations").add(save_data)
        doc_id = doc_ref[1].id  # 생성된 문서 ID 추출

        return {
            "message": "대화 저장 완료",
            "id": doc_id,
            "data": save_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 🗑️ DELETE - 특정 대화 삭제
# ─────────────────────────────────────────
@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    try:
        db = firestore.client()
        doc = db.collection("conversations").document(conversation_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="대화 기록을 찾을 수 없습니다")

        db.collection("conversations").document(conversation_id).delete()
        return {"message": "대화 삭제 완료", "id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 🗑️ DELETE - 세션 전체 삭제
# ─────────────────────────────────────────
@router.delete("/session/{session_id}")
def delete_session_conversations(session_id: str):
    try:
        db = firestore.client()
        docs = (
            db.collection("conversations")
            .where("session_id", "==", session_id)
            .stream()
        )
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"세션 {session_id} 대화 없음")

        return {
            "message": f"세션 대화 {deleted_count}개 삭제 완료",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))