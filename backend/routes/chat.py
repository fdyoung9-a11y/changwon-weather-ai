import os
import uuid                                      # 대화방 이름표 만들기용
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from routes.weather import get_weather_summary, get_all_weather
from routes.conversations import create_conversation, ConversationCreate

load_dotenv()

router = APIRouter()

# AI 연결 설정 (.env 또는 Render 환경 변수에서 읽기)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://copa.codyssey.kr/v1")
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str | None = None


# 값이 비어 있으면 "-"로 표시
def show(value):
    return "-" if value is None else value


# 월별 데이터를 표 형태 글자로 만들기 (AI에게 넘겨줄 자료)
def build_monthly_table() -> str:
    rows = get_all_weather()["data"]
    rows.sort(key=lambda d: (d["year"], d["month"]))   # 오래된 순서로 정렬

    lines = ["연-월 | 평균기온 | 최고기온 | 최저기온 | 강수량"]
    for d in rows:
        lines.append(
            f"{d['year']}-{d['month']:02d} | {show(d.get('avg_temp'))} | "
            f"{show(d.get('max_temp'))} | {show(d.get('min_temp'))} | {show(d.get('rainfall'))}"
        )
    return "\n".join(lines)


# 요약 + 월별 데이터를 넣어서 시스템 프롬프트 만들기
def build_system_prompt() -> str:
    try:
        s = get_weather_summary()
        m = s["metrics"]
        return (
            "당신은 창원 날씨 데이터 분석 비서입니다.\n\n"
            "[데이터 요약]\n"
            f"- 데이터 기간: {s['period']}\n"
            f"- 총 레코드: {s['count']}개 (월별 데이터)\n"
            f"- 전체 평균기온: {m['average_temp']}℃\n"
            f"- 최고기온: {m['highest_temp']}℃\n"
            f"- 최저기온: {m['lowest_temp']}℃\n"
            f"- 최근 트렌드: {s['trend']}\n\n"
            "[월별 데이터] (기온 단위: ℃)\n"
            f"{build_monthly_table()}\n\n"
            "답변 규칙:\n"
            "- 특정 연도·월 질문은 위 월별 데이터에서 찾아 숫자를 근거로 답하세요.\n"
            "- 계절은 봄 3~5월, 여름 6~8월, 가을 9~11월, 겨울 12~2월로 봅니다.\n"
            "- 비교 질문은 다른 해의 같은 기간과 비교해 주세요.\n"
            "- 데이터에 없는 내용은 추측하지 말고 모른다고 답하세요."
        )
    except Exception:
        return "당신은 창원 날씨 전문 AI 어시스턴트입니다. 현재 데이터를 불러오지 못했습니다."


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 대화방 이름표: 보내온 게 있으면 그대로, 없으면 새로 만들기
    session_id = request.conversation_id or str(uuid.uuid4())

    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": request.message}
        ]
    )
    ai_message = response.choices[0].message.content

    # Firestore에 자동 저장 (실패해도 답변은 돌려줌)
    try:
        create_conversation(ConversationCreate(
            user_message=request.message,
            bot_response=ai_message,
            session_id=session_id
        ))
    except Exception as e:
        print(f"[WARN] 대화 저장 실패: {e}")

    return ChatResponse(
        response=ai_message,
        conversation_id=session_id      # 대화방 이름표를 응답에 담아 보내기
    )


def get_ai_response(message: str) -> str:
    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content