"use client";

interface FocusAreaProps {
  topic: string;
  accuracy: number;
  questionsAttempted: number;
  trend?: "improving" | "declining" | "stable";
}

export default function FocusArea({ topic, accuracy, questionsAttempted, trend }: FocusAreaProps) {
  const accuracyColor =
    accuracy >= 70 ? "text-green-700 bg-green-100" :
    accuracy >= 40 ? "text-amber-700 bg-amber-100" :
    "text-red-700 bg-red-100";

  const barColor =
    accuracy >= 70 ? "bg-correct" :
    accuracy >= 40 ? "bg-warning" :
    "bg-wrong";

  const trendIcon = trend === "improving" ? "↑" : trend === "declining" ? "↓" : "→";
  const trendColor = trend === "improving" ? "text-green-500" : trend === "declining" ? "text-red-500" : "text-slate-400";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-700">{topic}</span>
        <div className="flex items-center gap-2">
          {trend && (
            <span className={`text-sm font-bold ${trendColor}`} aria-label={`Trend: ${trend}`}>
              {trendIcon}
            </span>
          )}
          <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${accuracyColor}`}>
            {accuracy}%
          </span>
        </div>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden" role="progressbar" aria-valuenow={accuracy} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={`h-full rounded-full transition-all duration-500 ${barColor}`}
          style={{ width: `${accuracy}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-slate-400">{questionsAttempted} questions attempted</p>
    </div>
  );
}