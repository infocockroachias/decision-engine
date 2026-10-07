"use client";

import { useState } from "react";

interface PaletteProps {
  totalQuestions: number;
  currentQuestion: number;
  answers: Record<number, { option: string; marked: boolean }>;
  onNavigate: (questionNum: number) => void;
}

export default function QuestionPalette({ totalQuestions, currentQuestion, answers, onNavigate }: PaletteProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatus = (num: number): "answered" | "marked" | "visited" | "unvisited" => {
    if (answers[num]?.marked) return "marked";
    if (answers[num]?.option) return "answered";
    if (num === currentQuestion) return "visited";
    return "unvisited";
  };

  const statusColors = {
    answered: "bg-correct text-white border-green-600",
    marked: "bg-warning text-white border-amber-600",
    visited: "bg-brand/10 text-brand border-brand",
    unvisited: "bg-slate-100 text-slate-500 border-slate-300 hover:border-slate-400",
  };

  const stats = {
    answered: Object.values(answers).filter(a => a.option).length,
    marked: Object.values(answers).filter(a => a.marked).length,
    remaining: totalQuestions - Object.values(answers).filter(a => a.option).length,
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {/* Toggle for mobile */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between sm:cursor-default sm:pointer-events-none"
        aria-expanded={isExpanded}
        aria-label="Toggle question palette"
      >
        <h3 className="text-sm font-semibold text-slate-900">Question Navigator</h3>
        <span className="sm:hidden text-slate-400">{isExpanded ? "▲" : "▼"}</span>
      </button>

      <div className={`mt-3 ${isExpanded ? "block" : "hidden"} sm:block`}>
        {/* Stats */}
        <div className="flex items-center gap-3 mb-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-correct" />
            <span className="text-xs text-slate-500">{stats.answered}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-warning" />
            <span className="text-xs text-slate-500">{stats.marked}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
            <span className="text-xs text-slate-500">{stats.remaining}</span>
          </div>
        </div>

        {/* Question Grid */}
        <div className="grid grid-cols-5 sm:grid-cols-6 gap-2" role="navigation" aria-label="Question navigation">
          {Array.from({ length: totalQuestions }, (_, i) => i + 1).map((num) => {
            const status = getStatus(num);
            const isCurrent = num === currentQuestion;
            return (
              <button
                key={num}
                onClick={() => onNavigate(num)}
                className={`flex h-9 w-full items-center justify-center rounded-lg border text-sm font-medium transition-all
                  ${statusColors[status]}
                  ${isCurrent ? "ring-2 ring-brand ring-offset-1" : ""}`}
                aria-label={`Question ${num} - ${status}`}
                aria-current={isCurrent ? "true" : undefined}
              >
                {num}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}