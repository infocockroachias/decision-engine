interface MistakeCardProps {
  questionNumber: number;
  questionText: string;
  userAnswer: string;
  correctAnswer: string;
  explanation: string;
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  missedReason?: string;
}

export default function MistakeCard({
  questionNumber,
  questionText,
  userAnswer,
  correctAnswer,
  explanation,
  topic,
  difficulty,
  missedReason,
}: MistakeCardProps) {
  const difficultyColor = {
    easy: "bg-green-100 text-green-700",
    medium: "bg-amber-100 text-amber-700",
    hard: "bg-red-100 text-red-700",
  }[difficulty];

  return (
    <div className="rounded-xl border border-red-200 bg-red-50/30 p-5 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center rounded-full bg-red-100 px-2.5 py-0.5 text-sm font-bold text-red-700">
            Q.{questionNumber}
          </span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${difficultyColor}`}>
            {difficulty}
          </span>
        </div>
        <span className="rounded-full bg-brand/10 px-2 py-0.5 text-xs font-medium text-brand">
          {topic}
        </span>
      </div>

      {/* Question */}
      <p className="mb-4 text-base font-medium text-slate-900">{questionText}</p>

      {/* Answers */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div className="rounded-lg border border-red-200 bg-white p-3">
          <p className="text-xs font-medium text-red-500 mb-1">Your Answer</p>
          <p className="font-semibold text-red-700">{userAnswer}</p>
        </div>
        <div className="rounded-lg border border-green-200 bg-white p-3">
          <p className="text-xs font-medium text-green-500 mb-1">Correct Answer</p>
          <p className="font-semibold text-green-700">{correctAnswer}</p>
        </div>
      </div>

      {/* Explanation */}
      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <p className="text-xs font-medium text-slate-500 mb-2">Explanation</p>
        <p className="text-sm text-slate-700 leading-relaxed">{explanation}</p>
      </div>

      {/* Missed Reason */}
      {missedReason && (
        <div className="mt-3 rounded-lg bg-amber-50 border border-amber-200 p-3">
          <p className="text-xs font-medium text-amber-600 mb-1">Why you likely missed it</p>
          <p className="text-sm text-amber-800">{missedReason}</p>
        </div>
      )}
    </div>
  );
}