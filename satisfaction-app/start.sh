#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "====================================="
echo "  만족도 설문 분석 앱 시작"
echo "====================================="

# ── 1. 한글 폰트 ──────────────────────────
if ! fc-list | grep -q "NanumGothic"; then
  echo "[1/4] 한글 폰트 설치 중..."
  sudo apt-get install -y fonts-nanum -q
  fc-cache -fv -q
else
  echo "[1/4] 한글 폰트 확인됨"
fi

# ── 2. Python 의존성 ───────────────────────
echo "[2/4] Python 패키지 설치 중..."
pip install -r "$BACKEND/requirements.txt" -q

# ── 3. .env 파일 ───────────────────────────
if [ ! -f "$BACKEND/.env" ]; then
  cp "$BACKEND/.env.example" "$BACKEND/.env"
  echo ""
  echo "⚠️  ANTHROPIC_API_KEY 를 입력해 주세요 (AI 코멘트에 사용)."
  echo "   API 키 없이도 기본 코멘트로 PDF 생성은 가능합니다."
  echo ""
  read -rp "   ANTHROPIC_API_KEY (없으면 Enter): " KEY
  if [ -n "$KEY" ]; then
    sed -i "s/your_key_here/$KEY/" "$BACKEND/.env"
    echo "   ✅ API 키 저장 완료"
  fi
fi

# ── 4. npm 의존성 ──────────────────────────
echo "[3/4] npm 패키지 설치 중..."
cd "$FRONTEND" && npm install -q

# ── 5. 실행 ───────────────────────────────
echo "[4/4] 서버 시작 중..."
echo ""

# 백엔드 백그라운드 실행
cd "$BACKEND"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 프론트엔드 백그라운드 실행
cd "$FRONTEND"
npm run dev &
FRONTEND_PID=$!

echo "====================================="
echo "  ✅ 앱이 실행되었습니다!"
echo ""
echo "  브라우저: http://localhost:5173"
echo "  백엔드:   http://localhost:8000"
echo ""
echo "  종료하려면 Ctrl+C 를 누르세요."
echo "====================================="

# Ctrl+C 시 두 프로세스 함께 종료
trap "echo ''; echo '앱 종료 중...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
