export default function ShapBar({ contributions, limit = 8 }) {
  const rows = [...contributions]
    .sort((a, b) => b.value - a.value)
    .slice(0, limit)
    .reverse();

  if (!rows.length) {
    return <p className="text-sm text-slate-400">No feature contributions available.</p>;
  }

  const maxAbs = Math.max(...rows.map((r) => Math.abs(r.value)), 1e-6);

  return (
    <div className="space-y-2.5">
      {rows.map((c) => {
        const v = c.value;
        const width = (Math.abs(v) / maxAbs) * 100;
        const positive = v >= 0;
        return (
          <div key={c.raw_feature || c.feature}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium truncate pr-2">{c.feature}</span>
              <span className={positive ? "text-red-400 font-semibold" : "text-emerald-400 font-semibold"}>
                {positive ? "+" : ""}
                {v.toFixed(3)}
              </span>
            </div>
            <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${positive ? "bg-red-500" : "bg-emerald-500"}`}
                style={{ width: `${width}%`, marginLeft: positive ? "50%" : undefined }}
              />
            </div>
          </div>
        );
      })}
      <div className="flex justify-between text-[10px] text-slate-500 pt-1">
        <span className="text-emerald-400">← lowers risk</span>
        <span>increases risk →</span>
      </div>
    </div>
  );
}
