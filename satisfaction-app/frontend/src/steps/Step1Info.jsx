import React from "react";

export default function Step1Info({ info, setInfo, onNext }) {
  const canProceed = info.program_name.trim().length > 0;

  return (
    <div className="card max-w-xl mx-auto">
      <h2 className="text-2xl font-bold text-brand-700 mb-2">프로그램 정보 입력</h2>
      <p className="text-gray-500 text-sm mb-8">AI 분석 코멘트 품질 향상을 위해 프로그램 정보를 입력해 주세요.</p>

      <div className="space-y-5">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            프로그램명 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="예: 2024년 진로탐색 캠프"
            value={info.program_name}
            onChange={(e) => setInfo((p) => ({ ...p, program_name: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">프로그램 목적</label>
          <textarea
            className="input-field resize-none"
            rows={3}
            placeholder="예: 청소년들의 자기이해 및 진로 방향성 탐색 기회 제공"
            value={info.program_purpose}
            onChange={(e) => setInfo((p) => ({ ...p, program_purpose: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">프로그램 목표</label>
          <textarea
            className="input-field resize-none"
            rows={3}
            placeholder="예: 참여자의 80% 이상이 진로 방향에 대한 긍정적 인식 형성"
            value={info.program_goal}
            onChange={(e) => setInfo((p) => ({ ...p, program_goal: e.target.value }))}
          />
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button className="btn-primary" onClick={onNext} disabled={!canProceed}>
          다음 단계 →
        </button>
      </div>
    </div>
  );
}
