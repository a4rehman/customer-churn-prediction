const SEGMENTS = [
  { max: 0.3, color: "#10b981" },
  { max: 0.5, color: "#f59e0b" },
  { max: 0.7, color: "#f97316" },
  { max: 1.0, color: "#ef4444" },
];

function polar(cx, cy, r, angleDeg) {
  const rad = (Math.PI / 180) * (angleDeg - 180);
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx, cy, r, startDeg, endDeg) {
  const s = polar(cx, cy, r, startDeg);
  const e = polar(cx, cy, r, endDeg);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
}

export default function ProbabilityGauge({ probability, label = "Churn Probability" }) {
  const p = Math.min(Math.max(probability || 0, 0), 1);
  const cx = 100;
  const cy = 95;
  const r = 74;

  let fillColor = "#10b981";
  for (const seg of SEGMENTS) {
    if (p <= seg.max) {
      fillColor = seg.color;
      break;
    }
  }

  const pct = p * 100;
  const startDeg = 0;
  const sweepDeg = 180 * pct / 100;
  const ticks = [0, 0.25, 0.5, 0.75, 1.0];

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 115" className="w-full max-w-[280px]">
        <path d={arcPath(cx, cy, r, 0, 180)} stroke="#334155" strokeWidth="14" fill="none" strokeLinecap="round" />
        {pct > 0.5 && (
          <path
            d={arcPath(cx, cy, r, startDeg, Math.min(sweepDeg, 180))}
            stroke={fillColor}
            strokeWidth="14"
            fill="none"
            strokeLinecap="round"
            style={{ transition: "d 0.6s ease" }}
          />
        )}
        {ticks.map((t) => {
          const deg = (t / 1.0) * 180;
          const inner = polar(cx, cy, r - 11, deg);
          const outer = polar(cx, cy, r - 3, deg);
          return (
            <line
              key={t}
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="#64748b"
              strokeWidth="1.5"
            />
          );
        })}
        {[0.3, 0.5, 0.7].map((t) => {
          const pt = polar(cx, cy, r - 30, (t / 1.0) * 180);
          return (
            <text
              key={t}
              x={pt.x}
              y={pt.y}
              fill="#64748b"
              fontSize="9"
              textAnchor="middle"
              dy="0.3em"
            >
              {Math.round(t * 100)}
            </text>
          );
        })}
        <text x={cx} y={cy - 6} textAnchor="middle" fontSize="30" fontWeight="800" fill="#f8fafc">
          {pct.toFixed(1)}%
        </text>
        <text x={cx} y={cy + 16} textAnchor="middle" fontSize="10" fill="#94a3b8" letterSpacing="1">
          {label.toUpperCase()}
        </text>
        {pct > 0.5 && (
          <line
            x1={cx}
            y1={cy}
            x2={polar(cx, cy, r - 24, sweepDeg).x}
            y2={polar(cx, cy, r - 24, sweepDeg).y}
            stroke="#e2e8f0"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        )}
      </svg>
    </div>
  );
}
