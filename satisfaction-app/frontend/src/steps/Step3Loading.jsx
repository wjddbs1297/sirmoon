import React, { useEffect, useState } from "react";

const STEPS = [
  { id: 1, label: "파일 파싱 중...", icon: "📂", duration: 1500 },
  { id: 2, label: "AI 코멘트 생성 중...", icon: "🤖", duration: 4000 },
  { id: 3, label: "PDF 생성 중...", icon: "📄", duration: 1500 },
];

export default function Step3Loading({ result }) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (result) {
      setActiveStep(3);
      return;
    }
    let elapsed = 0;
    const timers = STEPS.map((s, i) => {
      const t = setTimeout(() => setActiveStep(i + 1), elapsed);
      elapsed += s.duration;
      return t;
    });
    return () => timers.forEach(clearTimeout);
  }, [result]);

  return (
    <div className="card max-w-md mx-auto text-center">
      <h2 className="text-2xl font-bold text-brand-700 mb-2">보고서 생성 중</h2>
      <p className="text-gray-500 text-sm mb-10">잠시만 기다려 주세요. AI가 데이터를 분석하고 있습니다.</p>

      <div className="space-y-4 text-left">
        {STEPS.map((s, i) => {
          const done = activeStep > i;
          const active = activeStep === i;
          return (
            <div
              key={s.id}
              className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-500
                ${done ? "bg-green-50 border-green-200" : active ? "bg-brand-50 border-brand-200" : "bg-gray-50 border-gray-200"}`}
            >
              <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0
                ${done ? "bg-green-500 text-white" : active ? "bg-brand-500 text-white" : "bg-gray-200 text-gray-400"}`}>
                {done ? "✓" : s.id}
              </div>
              <div className="flex-1">
                <span className={`font-medium ${done ? "text-green-700" : active ? "text-brand-700" : "text-gray-400"}`}>
                  {s.icon} {s.label}
                </span>
                {active && (
                  <div className="mt-2 h-1.5 bg-brand-100 rounded-full overflow-hidden">
                    <div className="h-full bg-brand-500 rounded-full animate-pulse" style={{ width: "60%" }} />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {activeStep === 3 && !result && (
        <div className="mt-6 flex justify-center">
          <svg className="animate-spin h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
        </div>
      )}
    </div>
  );
}
