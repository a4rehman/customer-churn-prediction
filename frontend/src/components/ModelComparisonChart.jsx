export default function ModelComparisonChart({ metrics }) {
  const rows = Object.entries(metrics || {})
    .map(([name, m]) => ({
      name,
      auc: m.roc_auc || 0,
      f1: m.f1 || 0,
      precision: m.precision || 0,
      recall: m.recall || 0,
    }))
    .sort((a, b) => b.auc - a.auc);

  if (!rows.length) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wider text-slate-400">
            <th className="pb-3 pr-3">Model</th>
            <th className="pb-3 pr-3">ROC AUC</th>
            <th className="pb-3 pr-3">F1</th>
            <th className="pb-3 pr-3">Precision</th>
            <th className="pb-3">Recall</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.name} className={i === 0 ? "bg-indigo-500/10" : "border-t border-slate-700/60"}>
              <td className="py-2.5 pr-3 font-medium">
                {r.name}
                {i === 0 && (
                  <span className="ml-2 text-[10px] bg-indigo-500/30 text-indigo-200 px-1.5 py-0.5 rounded">BEST</span>
                )}
              </td>
              <td className="py-2.5 pr-3">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${r.auc * 100}%` }} />
                  </div>
                  <span className="font-semibold">{r.auc.toFixed(4)}</span>
                </div>
              </td>
              <td className="py-2.5 pr-3">{r.f1.toFixed(3)}</td>
              <td className="py-2.5 pr-3">{r.precision.toFixed(3)}</td>
              <td className="py-2.5">{r.recall.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
