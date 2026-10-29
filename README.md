# 🌤️ 창원 날씨 AI

창원시 2000년부터 쌓인 월별 기온 데이터를 바탕으로 질문에 답해 주는 **AI 날씨 비서**입니다.

- 🌐 서비스 주소: https://changwon-weather-ai-frontend.vercel.app
- ⚙️ API 서버: https://changwon-weather-ai.onrender.com
- 📄 API 문서: https://changwon-weather-ai.onrender.com/docs

> 무료 서버를 사용해서, 한동안 접속이 없으면 첫 응답까지 30초~1분 정도 걸릴 수 있습니다.

---

## 📌 프로젝트 소개

"2023년 8월은 몇 도였어?", "가장 추웠던 달은 언제야?"처럼 자연어로 물으면
AI가 Firestore에 저장된 **322개월(2000-01 ~ 2026-10) 기온 데이터**를 근거로 답합니다.
나눈 대화는 자동으로 저장되어 언제든 다시 볼 수 있습니다.

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 데이터 요약 | 전체 기간, 데이터 개수, 평균·최고·최저 기온, 기온 추세 표시 |
| AI 날씨 비서 | 월별 데이터를 바탕으로 연도·월·계절별 질문에 답변 |
| 대화 기록 | 질문과 답변을 Firestore에 자동 저장, 대화방별로 다시 보기 |
| 데이터 관리 | 월별 기온 데이터 조회·추가·수정·삭제 (CRUD) |

## 🛠️ 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 백엔드 | Python 3.11, FastAPI, Uvicorn |
| 데이터베이스 | Firebase Firestore |
| AI | OpenAI SDK + gemini-3-flash |
| 프론트엔드 | HTML, CSS, JavaScript |
| 배포 | Render(백엔드), Vercel(프론트엔드) |
| 버전 관리 | Git, GitHub |

## 📁 폴더 구조

```text
changwon-weather-ai/
├── backend/
│   ├── main.py              # 서버 시작, CORS·Firebase 설정, /health
│   ├── requirements.txt     # 필요한 라이브러리 목록
│   └── routes/
│       ├── weather.py       # 월별 기온 CRUD, 데이터 요약
│       ├── chat.py          # AI 질문·답변
│       └── conversations.py # 대화 기록 저장·조회·삭제
├── frontend/
│   ├── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── scripts/                 # 데이터 전처리, Firestore 업로드
└── data/                    # 창원 월별 기온 CSV
```

## 🔌 주요 API

| 메서드 | 주소 | 설명 |
|---|---|---|
| GET | `/health` | 서버 상태 확인 |
| GET | `/summary` | 전체 데이터 요약 |
| GET | `/` | 전체 월별 데이터 |
| GET | `/{year}` | 특정 연도 데이터 |
| GET | `/{year}/{month}` | 특정 월 데이터 |
| POST | `/` | 월별 데이터 추가 |
| PUT | `/{year}/{month}` | 월별 데이터 수정 |
| DELETE | `/{year}/{month}` | 월별 데이터 삭제 |
| POST | `/chat` | AI에게 질문 |
| GET | `/conversations/` | 전체 대화 기록 |

전체 목록과 직접 테스트는 `/docs`에서 할 수 있습니다.

## 💻 내 컴퓨터에서 실행하기

### 1. 준비
```bash
git clone https://github.com/fdyoung9-a11y/changwon-weather-ai.git
cd changwon-weather-ai
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. 환경 변수 (`backend/.env`)
```text
OPENAI_API_KEY=발급받은_API_키
OPENAI_API_BASE=https://copa.codyssey.kr/v1
FIREBASE_KEY_PATH=Firebase_서비스_계정_키_파일_경로
```
> `.env`와 Firebase 키 파일은 `.gitignore`로 GitHub에 올라가지 않습니다.

### 3. 실행 (터미널 2개)
```bash
# 터미널 1 - 백엔드
cd backend
uvicorn main:app --reload

# 터미널 2 - 프론트엔드
cd frontend
python -m http.server 5500
```
브라우저에서 http://localhost:5500 접속

## 🚀 배포 구성

| 항목 | Render (백엔드) | Vercel (프론트엔드) |
|---|---|---|
| Root Directory | `backend` | `frontend` |
| 실행 | `uvicorn main:app --host 0.0.0.0 --port $PORT` | 정적 파일 |
| 환경 변수 | `OPENAI_API_KEY`, `OPENAI_API_BASE`, `FIREBASE_SERVICE_ACCOUNT_JSON`, `ALLOWED_ORIGINS`, `PYTHON_VERSION` | 없음 |

- 프론트엔드는 접속 주소를 보고 **로컬이면 `localhost:8000`, 배포 사이트면 Render 서버**를 자동으로 사용합니다.
- 배포 서버에는 키 파일 대신 키 내용 전체를 `FIREBASE_SERVICE_ACCOUNT_JSON` 환경 변수로 넣습니다.

## 🔧 개발하며 해결한 문제

| 문제 | 원인 | 해결 |
|---|---|---|
| `/health` 접속 시 422 오류 | `/{year}` 주소가 먼저 등록되어 `health`를 연도로 해석 | `/health`를 라우터보다 먼저 등록 |
| 배포 사이트에서 데이터 불러오기 실패 | CORS 허용 목록에 Vercel 주소 없음 | `ALLOWED_ORIGINS`에 Vercel 주소 추가 |
| 대화 시간이 9시간 늦게 표시 | 배포 서버가 UTC 기준 시간 사용 | 저장 시 한국 시간(KST)으로 기록 |
| AI가 특정 연도·월 질문에 답하지 못함 | AI에게 요약 정보만 전달 | 322개월 월별 데이터를 함께 전달 |