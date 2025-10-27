# 🚀 SmartFlow 백엔드 빠른 시작 가이드

## 📦 1단계: 설치

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 🤖 2단계: AI 모델 설정

AI 모델 파일 (`models.pkl`)을 `ai_models/` 폴더에 넣어주세요.

```
backend/
└── ai_models/
    └── models.pkl  # 여기에 AI 모델 파일
```

**모델 파일이 없어도 실행됩니다!** (더미 모드로 동작)

## ⚙️ 3단계: 환경 변수 설정 (선택사항)

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 수정 (필요시)
nano .env
```

## 🎯 4단계: 실행

```bash
# 개발 모드 (자동 리로드)
python main.py

# 또는
uvicorn main:app --reload
```

## ✅ 5단계: 확인

브라우저에서 다음 URL을 열어보세요:

- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health
- **AI 데모**: http://localhost:8000/api/forecast/demo

## 🎉 완료!

이제 백엔드가 실행되고 있습니다!

---

## 🔧 문제 해결

### 1. 모듈 import 에러
```bash
# 의존성 다시 설치
pip install -r requirements.txt --force-reinstall
```

### 2. AI 모델 로드 실패
```
⚠️ AI 모델 없음 - 더미 모드로 실행
```
→ 정상입니다. 더미 데이터로 동작합니다.

### 3. 포트 이미 사용 중
```bash
# 다른 포트로 실행
uvicorn main:app --port 8001
```

### 4. CORS 에러
`.env` 파일에서 `ALLOWED_ORIGINS`에 프론트엔드 URL 추가:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📞 도움이 필요하신가요?

README.md를 참고하세요!
