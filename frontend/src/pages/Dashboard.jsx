import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  Brain,
  Clock,
  Gauge as GaugeIcon,
  TrendingUp,
  Users,
  Wallet,
} from "lucide-react";
import { api } from "../api/client";
import KpiCard from "../components/KpiCard";
import ModelComparisonChart from "../components/ModelComparisonChart";
import RiskBadge from "../components/RiskBadge";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [model, setModel] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [summary, setSummary] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [s, m, mm, sm] = await Promise.all([
          api.adminStats(),
          api.modelInfo(),
          api.adminModel(),
          api.predictionSummary(14),
        ]);
        setStats(s);
        setModel(m);
        setModelMetrics(mm);
        setSummary(sm);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <Loading />;

  const riskDist = stats?.risk_distribution || {};
  const totalPred = Object.values(riskDist).reduce((a, b) => a + b, 0) || 1;
  const maxPred = Math.max(...Object.values(riskDist), 1);

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight">Overview</h1>
        <p className="text-sm text-slate-400">Churn risk intelligence across your customer base</p>
        {error && (
          <p className="text-sm text-red-400 mt-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
            {error}
          </p>
        )}
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Total Customers"
          value={stats?.total_customers?.toLocaleString()}
          icon={Users}
          color="text-indigo-400"
          sub="In dataset"
        />
        <KpiCard
          title="Churn Rate"
          value={`${((stats?.churn_rate || 0) * 100).toFixed(1)}%`}
          icon={TrendingUp}
          color="text-rose-400"
          sub={`${stats?.at_risk_customers?.toLocaleString()} at risk`}
        />
        <KpiCard
          title="Predictions Today"
          value={stats?.predictions_today}
          icon={Clock}
          color="text-amber-400"
          sub="Model calls in last 24h"
        />
        <KpiCard
          title="Model ROC AUC"
          value={stats?.model_roc_auc?.toFixed(4)}
          icon={Brain}
          color="text-emerald-400"
          badge={
            <span className="text-[11px] bg-slate-700/60 px-2 py-0.5 rounded mt-2 inline-block">
              {stats?.model_name}
            </span>
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold">Risk Distribution</h2>
            <GaugeIcon className="h-4 w-4 text-slate-500" />
          </div>
          <div className="space-y-4">
            {["Very High", "High", "Medium", "Low"].map((cat) => {
              const count = riskDist[cat] || 0;
              const pct = totalPred ? (count / totalPred) * 100 : 0;
              const color =
                cat === "Very High"
                  ? "bg-red-500"
                  : cat === "High"
                  ? "bg-orange-500"
                  : cat === "Medium"
                  ? "bg-amber-500"
                  : "bg-emerald-500";
              return (
                <div key={cat}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-slate-300 font-medium">{cat}</span>
                    <span className="text-slate-400">
                      {count} · {pct.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${(count / maxPred) * 100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
          <p className="text-xs text-slate-500 mt-4">
            Distribution of customer churn-risk across recorded predictions.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            <h2 className="font-bold">Recent Predictions</h2>
          </div>
          <div className="space-y-2.5 max-h-[320px] overflow-y-auto">
            {(stats?.recent_predictions || []).map((p) => (
              <Link
                to={`/customers/${p.customer_id}`}
                key={p.id}
                className="flex items-center justify-between gap-2 rounded-lg bg-slate-800/50 px-3 py-2 hover:bg-slate-700/50 transition-colors"
              >
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate">{p.customer_id}</p>
                  <p className="text-[11px] text-slate-400">
                    {new Date(p.predicted_at).toLocaleString()}
                  </p>
                </div>
                <RiskBadge category={p.risk_category} probability={p.probability} />
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h2 className="font-bold mb-4">Model Comparison</h2>
          <ModelComparisonChart metrics={modelMetrics?.models} />
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Wallet className="h-4 w-4 text-slate-500" />
            <h2 className="font-bold">Model Info</h2>
          </div>
          {model && (
            <dl className="space-y-3 text-sm">
              <Row k="Model" v={model.model_name} />
              <Row k="Version" v={model.model_version} />
              <Row k="Trained" v={model.trained_at?.replace("T", " ")} />
              <Row k="Samples" v={model.n_samples?.toLocaleString()} />
              <Row k="Encoded features" v={model.n_features} />
              <Row k="Selected features" v={model.n_selected_features} />
              <Row k="ROC AUC" v={model.roc_auc?.toFixed(4)} />
              <Row k="PR AUC" v={model.pr_auc?.toFixed(4)} />
            </dl>
          )}
        </div>
      </div>
    </div>
  );
}

function Row({ k, v }) {
  return (
    <div className="flex justify-between border-b border-slate-700/50 pb-2">
      <dt className="text-slate-400">{k}</dt>
      <dd className="font-semibold truncate max-w-[60%]">{v ?? "—"}</dd>
    </div>
  );
}

function Loading() {
  return (
    <div className="p-6 flex items-center justify-center h-64">
      <div className="animate-spin h-8 w-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
    </div>
  );
}
