import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import weather, chat, conversations   # ✅ 5번줄
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# .env 로드
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화
key_path = os.getenv("FIREBASE_KEY_PATH")
print(f"[DEBUG] FIREBASE_KEY_PATH = {key_path}")

cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)

# 라우터 등록
app.include_router(weather.router)
app.include_router(chat.router)
app.include_router(conversations.router, prefix="/conversations")  # ✅ 36번줄