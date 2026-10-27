from fastapi import APIRouter
from pydantic import BaseModel
from firebase_admin import firestore
from openai import OpenAI
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# ✅ Firestore에서 날씨 데이터 가져오기
def get_weather_context():
    db = firestore.client()
    try:
        docs = db.collection("monthly_weather").stream()
        lines = []
        for doc in docs:
            d = doc.to_dict()
            lines.append(
                f"{d['year']}년 {d['month']}월 - "
                f"평균기온: {d['avg_temp']}°C, "
                f"최고기온: {d['max_temp']}°C, "
                f"최저기온: {d['min_temp']}°C"
            )
        return "\n".join(lines)
    except Exception as e:
        return ""

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "API 키가 설정되지 않았습니다"}

        client = OpenAI(api_key=api_key)

        # ✅ 날씨 데이터 포함
        weather_data = get_weather_context()

        system_prompt = f"""
당신은 창원시의 기온 데이터를 분석하는 AI 비서입니다.
아래는 창원시의 월별 기온 데이터입니다. 이 데이터를 바탕으로 사용자 질문에 친절하게 답변하세요.
데이터에 없는 내용은 모른다고 솔직하게 말해주세요.

[창원시 월별 기온 데이터]
{weather_data}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content
        return {"response": answer}

    except Exception as e:
        return {"error": f"오류 발생: {str(e)}"}