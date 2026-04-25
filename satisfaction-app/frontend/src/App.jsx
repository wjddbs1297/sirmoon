import React, { useState } from "react";
import Step1Info from "./steps/Step1Info.jsx";
import Step2Upload from "./steps/Step2Upload.jsx";
import Step3Loading from "./steps/Step3Loading.jsx";
import Step4Done from "./steps/Step4Done.jsx";

const STEP_LABELS = ["프로그램 정보", "파일 업로드", "분석 중", "완료"];

export default function App() {
  const [step, setStep] = useState(1);
  const [info, setInfo] = useState({
    program_name: "",
    program_purpose: "",
    program_goal: "",
  });
  const [result, setResult] = useState(null);

  const handleAnalyze = (data) => {
    setResult(data);
    setStep(4);
  };

  const handleReset = () => {
    setStep(1);
    setInfo({ program_name: "", program_purpose: "", program_goal: "" });
    setResult(null);
  };

  return (
    <div className="min-h-screen py-10 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Logo / Title */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-brand-700 mb-1">
            📋 만족도 설문 분석기
          </h1>
          <p className="text-gray-500 text-sm">
            xlsx 파일 업로드 → AI 분석 → PDF 보고서 자동 생성
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center gap-0 mb-10">
          {STEP_LABELS.map((label, i) => {
            const num = i + 1;
            const done = step > num;
            const active = step === num;
            return (
              <React.Fragment key={num}>
                <div className="flex flex-col items-center">
                  <div className={`step-indicator text-sm
                    ${done ? "bg-green-500 text-white" : active ? "bg-brand-500 text-white" : "bg-gray-200 text-gray-400"}`}>
                    {done ? "✓" : num}
                  </div>
                  <span className={`text-xs mt-1 font-medium
                    ${active ? "text-brand-700" : done ? "text-green-600" : "text-gray-400"}`}>
                    {label}
                  </span>
                </div>
                {i < STEP_LABELS.length - 1 && (
                  <div className={`h-0.5 w-12 mx-1 mb-4 rounded transition-all
                    ${step > num ? "bg-green-400" : "bg-gray-200"}`} />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Step Content */}
        {step === 1 && (
          <Step1Info info={info} setInfo={setInfo} onNext={() => setStep(2)} />
        )}
        {step === 2 && (
          <Step2Upload
            info={info}
            onAnalyze={(data) => { setStep(3); setTimeout(() => handleAnalyze(data), 500); }}
            onBack={() => setStep(1)}
          />
        )}
        {step === 3 && <Step3Loading result={result} />}
        {step === 4 && (
          <Step4Done result={result} programName={info.program_name} onReset={handleReset} />
        )}
      </div>
    </div>
  );
}
