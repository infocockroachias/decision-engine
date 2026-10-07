"use client";

interface SubjectData {
  name: string;
  correct: number;
  wrong: number;
  skipped: number;
  color: string;
}

interface SubjectPieChartProps {
  data: SubjectData[];
  title?: string;
}

function calculatePercentage(part: number, total: number): number {
  return total === 0 ? 0 : Math.round((part / total) * 100);
}

function generateDonutSegment(percentage: number, offset: number): { d: string; dashOffset: number } {
  const circumference = 2 * Math.PI * 40;
  const dashLength = (percentage / 100) * circumference;
  return {
    d: `M 50 10 A 40 40 0 ${percentage > 50 ? 1 : 0} 1 ${50 + 40 * Math.cos(-Math.PI / 2 + (offset / 100) * 2 * Math.PI)} ${50 + 40 * Math.sin(-Math.PI / 2 + (offset / 100) * 2 * Math.PI)}`,
    dashOffset: offset,
  };
}

export default function SubjectPieChart({ data, title = "Subject-wise Performance" }: SubjectPieChartProps) {
  const totalCorrect = data.reduce((sum, s) => sum + s.correct, 0);
  const totalWrong = data.reduce((sum, s) => sum + s.wrong, 0);
  const totalSkipped = data.reduce((sum, s) => sum + s.skipped, 0);
  const grandTotal = totalCorrect + totalWrong + totalSkipped;

  let cumulativeOffset = 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-900">{title}</h3>

      {/* Donut Chart */}
      <div className="flex flex-col items-center sm:flex-row sm:items-start gap-6">
        <div className="relative">
          <svg width="100" height="100" viewBox="0 0 100 100" className="transform -rotate-90">
            {/* Background circle */}
            <circle cx="50" cy="50" r="40" fill="none" stroke="#f1f5f9" strokeWidth="12" />
            {/* Segments for correct answers */}
            {data.map((subject, i) => {
              const total = subject.correct + subject.wrong + subject.skipped;
              const correctPct = calculatePercentage(subject.correct, grandTotal);
              const wrongPct = calculatePercentage(subject.wrong, grandTotal);
              const skippedPct = calculatePercentage(subject.skipped, grandTotal);
              const circumference = 2 * Math.PI * 40;

              const correctLength = (correctPct / 100) * circumference;
              const wrongLength = (wrongPct / 100) * circumference;
              const skippedLength = (skippedPct / 100) * circumference;

              const segments = (
                <g key={subject.name}>
                  <circle
                    cx="50" cy="50" r="40"
                    fill="none"
                    stroke={subject.color}
                    strokeWidth="12"
                    strokeDasharray={`${correctLength} ${circumference - correctLength}`}
                    strokeDashoffset={-(cumulativeOffset / 100) * circumference}
                    opacity="0.9"
                  />
                  <circle
                    cx="50" cy="50" r="40"
                    fill="none"
                    stroke="#dc143c"
                    strokeWidth="12"
                    strokeDasharray={`${wrongLength} ${circumference - wrongLength}`}
                    strokeDashoffset={-((cumulativeOffset + correctPct) / 100) * circumference}
                    opacity="0.5"
                  />
                </g>
              );

              cumulativeOffset += correctPct + wrongPct;
              return segments;
            })}
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-sm font-bold text-slate-700">
              {grandTotal > 0 ? Math.round((totalCorrect / grandTotal) * 100) : 0}%
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-2">
          {data.map((subject) => {
            const total = subject.correct + subject.wrong + subject.skipped;
            const accuracy = total > 0 ? Math.round((subject.correct / total) * 100) : 0;
            return (
              <div key={subject.name} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: subject.color }} />
                  <span className="text-sm text-slate-700">{subject.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-green-600">{subject.correct}✓</span>
                  <span className="text-xs text-red-600">{subject.wrong}✗</span>
                  <span className="text-xs text-slate-400">{subject.skipped}—</span>
                  <span className="text-xs font-semibold text-slate-600 w-8 text-right">{accuracy}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary bar */}
      <div className="mt-4 flex items-center gap-4 border-t border-slate-100 pt-4">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-correct" />
          <span className="text-xs text-slate-500">Correct: {totalCorrect}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-wrong" />
          <span className="text-xs text-slate-500">Wrong: {totalWrong}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-slate-300" />
          <span className="text-xs text-slate-500">Skipped: {totalSkipped}</span>
        </div>
      </div>
    </div>
  );
}