const riskColors = {
  "Very High": { text: "text-red-400", bg: "bg-red-500/15 border-red-500/40", dot: "bg-red-500" },
  High: { text: "text-orange-400", bg: "bg-orange-500/15 border-orange-500/40", dot: "bg-orange-500" },
  Medium: { text: "text-amber-400", bg: "bg-amber-500/15 border-amber-500/40", dot: "bg-amber-500" },
  Low: { text: "text-emerald-400", bg: "bg-emerald-500/15 border-emerald-500/40", dot: "bg-emerald-500" },
};

export default function RiskBadge({ category, probability }) {
  const c = riskColors[category] || riskColors.Medium;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-semibold ${c.text} ${c.bg}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {category}
      {probability !== undefined && (
        <span className="opacity-70 font-normal">
          · {(probability * 100).toFixed(1)}%
        </span>
      )}
    </span>
  );
}
