import os
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://copa.codyssey.kr/v1"
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[
            {"role": "system", "content": "당신은 창원 날씨 전문 AI 어시스턴트입니다."},
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
            {"role": "system", "content": "당신은 창원 날씨 전문 AI 어시스턴트입니다."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content