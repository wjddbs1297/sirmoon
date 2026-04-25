import os
import uuid
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from parser import parse_xlsx
from analyzer import analyze
from ai_comment import generate_comments
from pdf_builder import build_pdf

app = FastAPI(title="Survey Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = Path(tempfile.gettempdir()) / "survey_reports"
REPORTS_DIR.mkdir(exist_ok=True)


@app.post("/api/analyze")
async def analyze_survey(
    file: UploadFile = File(...),
    program_name: str = Form(...),
    program_purpose: str = Form(default=""),
    program_goal: str = Form(default=""),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="xlsx 또는 xls 파일만 업로드 가능합니다.")

    file_bytes = await file.read()

    try:
        parsed = parse_xlsx(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"파일 파싱 오류: {str(e)}")

    if not parsed["questions"]:
        raise HTTPException(status_code=422, detail="5점 척도 문항을 감지할 수 없습니다. 파일 형식을 확인해 주세요.")

    stats = analyze(parsed)

    ai_comments = generate_comments(
        program_name=program_name,
        program_purpose=program_purpose,
        program_goal=program_goal,
        stats=stats,
        free_texts=parsed["free_texts"],
    )

    pdf_bytes = build_pdf(
        program_name=program_name,
        program_purpose=program_purpose,
        program_goal=program_goal,
        stats=stats,
        ai_comments=ai_comments,
        free_texts=parsed["free_texts"],
    )

    report_id = str(uuid.uuid4())
    pdf_path = REPORTS_DIR / f"{report_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)

    return JSONResponse({
        "report_id": report_id,
        "pdf_url": f"/api/download/{report_id}",
        "preview_data": {
            "total_count": stats["total"],
            "questions": stats["questions"],
            "overall_avg": stats["overall_avg"],
            "overall_positive_rate": stats["overall_positive_rate"],
        },
    })


@app.get("/api/download/{report_id}")
async def download_report(report_id: str):
    pdf_path = REPORTS_DIR / f"{report_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename="survey_report.pdf",
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ── Static frontend (production) ────────────────────────────────
_static = Path(__file__).parent / "static"
if _static.exists():
    app.mount("/assets", StaticFiles(directory=str(_static / "assets")), name="assets")

    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(str(_static / "index.html"))
