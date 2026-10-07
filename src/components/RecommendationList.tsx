interface Recommendation {
  id: string;
  type: "improvement" | "strength" | "practice" | "resource";
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  subject?: string;
}

interface RecommendationListProps {
  recommendations: Recommendation[];
}

const typeConfig = {
  improvement: { icon: "📈", color: "bg-red-100 text-red-700 border-red-200" },
  strength: { icon: "💪", color: "bg-green-100 text-green-700 border-green-200" },
  practice: { icon: "📝", color: "bg-blue-100 text-blue-700 border-blue-200" },
  resource: { icon: "📚", color: "bg-purple-100 text-purple-700 border-purple-200" },
};

const priorityBadge = {
  high: "bg-red-500 text-white",
  medium: "bg-amber-500 text-white",
  low: "bg-slate-400 text-white",
};

export default function RecommendationList({ recommendations }: RecommendationListProps) {
  const highPriority = recommendations.filter((r) => r.priority === "high");
  const others = recommendations.filter((r) => r.priority !== "high");

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-slate-900">Personalized Recommendations</h3>

      {highPriority.length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-red-500">
            Priority Focus Areas
          </p>
          <div className="space-y-3">
            {highPriority.map((rec) => (
              <RecommendationItem key={rec.id} recommendation={rec} />
            ))}
          </div>
        </div>
      )}

      {others.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Additional Suggestions
          </p>
          <div className="space-y-3">
            {others.map((rec) => (
              <RecommendationItem key={rec.id} recommendation={rec} />
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 && (
        <p className="text-center text-sm text-slate-400 py-4">
          No recommendations yet. Complete a test to get personalized insights.
        </p>
      )}
    </div>
  );
}

function RecommendationItem({ recommendation }: { recommendation: Recommendation }) {
  const config = typeConfig[recommendation.type];

  return (
    <div className={`rounded-lg border p-4 ${config.color}`}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg" aria-hidden="true">{config.icon}</span>
          <span className="font-semibold text-sm">{recommendation.title}</span>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${priorityBadge[recommendation.priority]}`}>
          {recommendation.priority}
        </span>
      </div>
      <p className="text-sm opacity-80 leading-relaxed">{recommendation.description}</p>
      {recommendation.subject && (
        <span className="mt-2 inline-block rounded bg-white/50 px-2 py-0.5 text-xs font-medium">
          {recommendation.subject}
        </span>
      )}
    </div>
  );
}