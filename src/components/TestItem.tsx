"use client";

interface TestItemProps {
  id: string;
  title: string;
  date: string;
  score: number;
  totalMarks: number;
  subjects: string[];
  status: "completed" | "in-progress" | "pending";
  onResume?: () => void;
  onViewResults?: () => void;
}

export default function TestItem({ id, title, date, score, totalMarks, subjects, status, onResume, onViewResults }: TestItemProps) {
  const percentage = Math.round((score / totalMarks) * 100);
  const statusLabel = {
    completed: { text: "Completed", color: "bg-green-100 text-green-700" },
    "in-progress": { text: "In Progress", color: "bg-amber-100 text-amber-700" },
    pending: { text: "Pending", color: "bg-slate-100 text-slate-600" },
  }[status];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="font-semibold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{date}</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusLabel.color}`}>
          {statusLabel.text}
        </span>
      </div>

      {/* Subjects */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {subjects.map((s) => (
          <span key={s} className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{s}</span>
        ))}
      </div>

      {/* Score */}
      {status === "completed" && (
        <div className="flex items-center gap-3 mb-3">
          <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
            <div
              className={`h-full rounded-full ${percentage >= 60 ? "bg-correct" : percentage >= 40 ? "bg-warning" : "bg-wrong"}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <span className="text-sm font-bold text-slate-700">{score}/{totalMarks}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {status === "in-progress" && onResume && (
          <button
            onClick={onResume}
            className="flex-1 rounded-lg bg-brand px-3 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors"
          >
            Resume Test
          </button>
        )}
        {status === "completed" && onViewResults && (
          <button
            onClick={onViewResults}
            className="flex-1 rounded-lg bg-brand/10 px-3 py-2 text-sm font-medium text-brand hover:bg-brand/20 transition-colors"
          >
            View Results
          </button>
        )}
      </div>
    </div>
  );
}