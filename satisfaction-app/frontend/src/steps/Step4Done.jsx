import React from "react";
import { API_BASE } from "../api.js";

export default function Step4Done({ result, programName, onReset }) {
  const handleDownload = () => {
    window.open(`${API_BASE}${result.pdf_url}`, "_blank");
  };

  const preview = result.preview_data || {};

  return (
    <div className="card max-w-lg mx-auto text-center">
      <div className="text-6xl mb-4">🎉</div>
      <h2 className="text-2xl font-bold text-brand-700 mb-2">보고서 생성 완료!</h2>
      <p className="text-gray-500 text-sm mb-8">{programName} 만족도 분석 보고서가 준비되었습니다.</p>

      <div className="grid grid-cols-3 gap-3 mb-8">
        <div className="bg-brand-50 border border-brand-100 rounded-xl p-4">
          <div className="text-2xl font-bold text-brand-700">{preview.total_count ?? "-"}</div>
          <div className="text-xs text-gray-500 mt-1">총 응답자</div>
        </div>
        <div className="bg-brand-50 border border-brand-100 rounded-xl p-4">
          <div className="text-2xl font-bold text-brand-700">{preview.overall_avg ?? "-"}</div>
          <div className="text-xs text-gray-500 mt-1">전체 평균 점수</div>
        </div>
        <div className="bg-brand-50 border border-brand-100 rounded-xl p-4">
          <div className="text-2xl font-bold text-brand-700">{preview.overall_positive_rate ?? "-"}%</div>
          <div className="text-xs text-gray-500 mt-1">긍정 응답률</div>
        </div>
      </div>

      {preview.questions && preview.questions.length > 0 && (
        <div className="bg-gray-50 rounded-xl p-4 mb-8 text-left">
          <p className="text-sm font-semibold text-gray-700 mb-3">감지된 문항 ({preview.questions.length}개)</p>
          <ul className="space-y-1">
            {preview.questions.map((q, i) => (
              <li key={i} className="text-xs text-gray-500 flex gap-2">
                <span className="text-brand-500 font-bold flex-shrink-0">Q{i + 1}</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-3">
        <button className="btn-primary w-full text-lg py-4" onClick={handleDownload}>
          📥 PDF 보고서 다운로드
        </button>
        <button className="btn-secondary w-full" onClick={onReset}>
          새 보고서 만들기
        </button>
      </div>
    </div>
  );
}
