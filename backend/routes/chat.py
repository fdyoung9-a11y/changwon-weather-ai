import os
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from routes.weather import get_weather_summary   # ✨ 새로 추가: 요약 함수 불러오기

load_dotenv()

router = APIRouter()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://copa.codyssey.kr/v1"
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str | None = None


# ✨ 새로 추가: 요약 데이터를 넣어서 시스템 프롬프트 만들기
def build_system_prompt() -> str:
    try:
        s = get_weather_summary()   # 요약 API와 같은 계산 결과를 받아와요
        m = s["metrics"]
        return (
            "당신은 창원 날씨 데이터 분석 비서입니다.\n\n"
            "[사용자 데이터 요약]\n"
            f"- 데이터 기간: {s['period']}\n"
            f"- 총 레코드: {s['count']}개 (월별 데이터)\n"
            f"- 전체 평균기온: {m['average_temp']}℃\n"
            f"- 최고기온: {m['highest_temp']}℃\n"
            f"- 최저기온: {m['lowest_temp']}℃\n"
            f"- 최근 트렌드: {s['trend']}\n\n"
            "위 데이터를 기반으로 맞춤형 답변을 제공하세요. "
            "데이터에 없는 내용은 추측하지 말고 모른다고 답하세요."
        )
    except Exception:
        # 요약을 못 불러와도 챗봇은 멈추지 않도록 기본 문장을 사용해요
        return "당신은 창원 날씨 전문 AI 어시스턴트입니다. 현재 데이터 요약을 불러오지 못했습니다."


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[
            {"role": "system", "content": build_system_prompt()},   # ✨ 바뀐 부분
            {"role": "user", "content": request.message}
        ]
    )
    ai_message = response.choices[0].message.content
    return ChatResponse(
        response=ai_message,
        conversation_id=request.conversation_id
    )

def get_ai_response(message: str) -> str:
    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[
            {"role": "system", "content": build_system_prompt()},   # ✨ 바뀐 부분
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content