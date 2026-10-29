import os
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import weather, chat, conversations
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# .env 로드 (내 컴퓨터에서만 사용, 서버에서는 환경 변수를 직접 설정)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = FastAPI()

# ✨ CORS 설정: 허용할 주소를 환경 변수에서 읽기 (여러 개는 쉼표로 구분)
origins_text = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
allowed_origins = [o.strip() for o in origins_text.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✨ Firebase 초기화
# - 서버(Render): FIREBASE_SERVICE_ACCOUNT_JSON 에 키 파일 내용 전체
# - 내 컴퓨터:    FIREBASE_KEY_PATH 에 키 파일 경로
key_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
if key_json:
    cred = credentials.Certificate(json.loads(key_json))
else:
    cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH"))
firebase_admin.initialize_app(cred)

# ✨ 서버 상태 확인용 (라우터보다 먼저 등록해야 /{year} 주소에 가로채이지 않음)
@app.get("/health")
def health():
    return {"status": "ok"}


# 라우터 등록
app.include_router(weather.router)
app.include_router(chat.router)
app.include_router(conversations.router, prefix="/conversations")