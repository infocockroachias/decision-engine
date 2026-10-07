interface ScoreCardProps {
  label: string;
  value: number | string;
  sublabel?: string;
  variant?: "default" | "correct" | "wrong" | "warning";
}

export default function ScoreCard({ label, value, sublabel, variant = "default" }: ScoreCardProps) {
  const bgColor = {
    default: "bg-white border-slate-200",
    correct: "bg-green-50 border-green-300",
    wrong: "bg-red-50 border-red-300",
    warning: "bg-amber-50 border-amber-300",
  }[variant];

  const textColor = {
    default: "text-slate-900",
    correct: "text-green-700",
    wrong: "text-red-700",
    warning: "text-amber-700",
  }[variant];

  return (
    <div className={`rounded-xl border p-4 shadow-sm ${bgColor}`}>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${textColor}`}>{value}</p>
      {sublabel && <p className="mt-1 text-xs text-slate-400">{sublabel}</p>}
    </div>
  );
}