export default function KpiCard({ title, value, sub, icon: Icon, color = "text-indigo-400", badge }) {
  return (
    <div className="card flex items-start justify-between">
      <div className="min-w-0">
        <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">{title}</p>
        <p className="text-3xl font-extrabold mt-2 truncate">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        {badge}
      </div>
      {Icon && (
        <div className={`h-11 w-11 rounded-xl flex items-center justify-center bg-slate-700/50 ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
