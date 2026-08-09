import { AlertTriangle, BadgeDollarSign, Lightbulb, Star, UserPlus } from "lucide-react";

const priorityStyle = {
  high: "border-red-500/40 bg-red-500/10 text-red-300",
  medium: "border-amber-500/40 bg-amber-500/10 text-amber-300",
  low: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
};

const iconByCategory = {
  contract: Star,
  pricing: BadgeDollarSign,
  upsell: UserPlus,
  retention: Lightbulb,
  billing: BadgeDollarSign,
};

export default function Recommendations({ recommendations }) {
  if (!recommendations?.length) {
    return <p className="text-sm text-slate-400">No recommendations generated.</p>;
  }

  return (
    <div className="space-y-2.5">
      {recommendations.map((rec, idx) => {
        const Icon = iconByCategory[rec.category] || Lightbulb;
        return (
          <div
            key={idx}
            className={`flex gap-3 rounded-lg border p-3 ${priorityStyle[rec.priority] || priorityStyle.low}`}
          >
            <div className="mt-0.5">
              <Icon className="h-4.5 w-4.5 h-[18px] w-[18px]" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold">{rec.title}</p>
                <span className="text-[10px] uppercase tracking-wide opacity-70">{rec.priority}</span>
              </div>
              <p className="text-xs opacity-80 mt-0.5">{rec.reason}</p>
              <p className="text-[11px] mt-1 font-medium">{rec.impact}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
