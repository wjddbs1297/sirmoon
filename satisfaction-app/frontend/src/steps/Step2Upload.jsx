import React, { useRef, useState } from "react";
import { API_BASE } from "../api.js";

export default function Step2Upload({ info, onAnalyze, onBack }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const [previewError, setPreviewError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.match(/\.(xlsx|xls)$/i)) {
      setPreviewError("xlsx 또는 xls 파일만 업로드 가능합니다.");
      return;
    }
    setFile(f);
    setPreview(null);
    setPreviewError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    handleFile(f);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setUploading(true);
    setPreviewError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("program_name", info.program_name);
    formData.append("program_purpose", info.program_purpose);
    formData.append("program_goal", info.program_goal);

    try {
      const res = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "분석 중 오류가 발생했습니다.");
      }
      const data = await res.json();
      onAnalyze(data);
    } catch (e) {
      setPreviewError(e.message);
      setUploading(false);
    }
  };

  return (
    <div className="card max-w-xl mx-auto">
      <h2 className="text-2xl font-bold text-brand-700 mb-2">설문 파일 업로드</h2>
      <p className="text-gray-500 text-sm mb-8">Google Forms에서 내보낸 xlsx 파일을 업로드하세요.</p>

      <div
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200
          ${dragging ? "border-brand-500 bg-brand-50" : "border-gray-300 hover:border-brand-500 hover:bg-brand-50"}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="text-4xl mb-3">📊</div>
        {file ? (
          <div>
            <p className="font-semibold text-brand-700 text-lg">{file.name}</p>
            <p className="text-gray-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div>
            <p className="text-gray-600 font-medium">파일을 드래그하거나 클릭하여 선택</p>
            <p className="text-gray-400 text-sm mt-1">xlsx, xls 파일 지원</p>
          </div>
        )}
      </div>

      {previewError && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          ⚠️ {previewError}
        </div>
      )}

      <div className="mt-4 bg-brand-50 border border-brand-100 rounded-xl p-4 text-sm text-brand-700">
        <p className="font-semibold mb-1">📋 지원 파일 구조</p>
        <p className="text-xs text-gray-500">Row 0: 컬럼 헤더 | Row 1: 문항 텍스트 | Row 2~: 응답 데이터</p>
        <p className="text-xs text-gray-500 mt-1">5점 척도(매우동의함~매우동의하지않음), 성별, 자유응답 자동 감지</p>
      </div>

      <div className="mt-8 flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← 이전</button>
        <button
          className="btn-primary"
          onClick={handleAnalyze}
          disabled={!file || uploading}
        >
          {uploading ? "처리 중..." : "분석 시작 →"}
        </button>
      </div>
    </div>
  );
}
