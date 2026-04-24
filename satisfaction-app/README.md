# 만족도 설문 자동 분석 & PDF 보고서 생성 앱

## 빠른 시작

### 1. 한글 폰트 설치
```bash
sudo apt-get install -y fonts-nanum
fc-cache -fv
```

### 2. 백엔드 실행
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY 설정
uvicorn main:app --reload --port 8000
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

브라우저에서 http://localhost:5173 접속

## 지원 xlsx 구조
- Row 0: 컬럼 헤더 (응답일시, 참여자, 학교명, 성별, 문항들...)
- Row 1: 문항 텍스트 (빈칸이면 Row 0 헤더 사용)
- Row 2~: 실제 응답 데이터

## 5점 척도 응답값
`매우 동의함` / `동의함` / `보통` / `동의하지 않음` / `매우 동의하지 않음`
