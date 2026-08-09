import { useEffect, useState } from "react";
import {
  Bar,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ShieldPlus, Users } from "lucide-react";
import { api } from "../api/client";
import AuthImage from "../components/AuthImage";

export default function Admin() {
  const [modelMetrics, setModelMetrics] = useState(null);
  const [eda, setEda] = useState(null);
  const [summary, setSummary] = useState([]);
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ username: "", email: "", password: "", role: "viewer" });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [mm, e, s, u] = await Promise.all([
          api.adminModel(),
          api.adminEda(),
          api.predictionSummary(14),
          api.adminUsers(),
        ]);
        setModelMetrics(mm);
        setEda(e);
        setSummary(s);
        setUsers(u);
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, []);

  const createUser = async (e) => {
    e.preventDefault();
    setMsg("");
    setErr("");
    try {
      const created = await api.createUser(newUser);
      setUsers((prev) => [...prev, created]);
      setMsg(`User ${created.username} created`);
      setNewUser({ username: "", email: "", password: "", role: "viewer" });
    } catch (error) {
      setErr(error.message);
    }
  };

  const best = modelMetrics?.best || {};
  const catChurn = eda?.categorical_churn_rate || {};
  const contractData = Object.entries(catChurn.Contract || {}).map(([name, value]) => ({
    name,
    "Churn rate": (value * 100).toFixed(1),
  }));

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight">Admin Console</h1>
        <p className="text-sm text-slate-400">Model performance, EDA insights, and platform administration</p>
        {err && <p className="text-sm text-red-400 mt-2">{err}</p>}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h2 className="font-bold mb-3">Best Model</h2>
          <div className="space-y-2 text-sm">
            <p className="text-xl font-extrabold text-indigo-300">{best.best_model}</p>
            <Row k="Accuracy" v={best.accuracy} />
            <Row k="Precision" v={best.precision} />
            <Row k="Recall" v={best.recall} />
            <Row k="F1" v={best.f1} />
            <Row k="ROC AUC" v={best.roc_auc} />
            <Row k="PR AUC" v={best.pr_auc} />
            <Row k="Selected features" v={best.feature_selection?.selected_features} />
          </div>
        </div>

        <div className="card">
          <h2 className="font-bold mb-3">Confusion Matrix</h2>
          <AuthImage src={api.reportImage("confusion_matrix.png")} className="rounded-lg w-full" alt="Confusion matrix" />
        </div>

        <div className="card">
          <h2 className="font-bold mb-3">Prediction Volume (14d)</h2>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
                <Line type="monotone" dataKey="predictions" stroke="#6366f1" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="high_risk" stroke="#ef4444" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h2 className="font-bold mb-3">ROC & Precision-Recall</h2>
          <AuthImage src={api.reportImage("roc_pr_curves.png")} className="rounded-lg w-full" alt="ROC and PR curves" />
        </div>
        <div className="card">
          <h2 className="font-bold mb-3">SHAP Feature Importance</h2>
          <AuthImage src={api.reportImage("shap_summary.png")} className="rounded-lg w-full" alt="SHAP summary" />
        </div>
        <div className="card">
          <h2 className="font-bold mb-3">Churn Rate by Contract</h2>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart contractData={contractData} />
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-bold mb-3">EDA Insights</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-xs uppercase text-slate-400">Rows</p>
            <p className="font-bold">{eda?.rows?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-400">Churn Rate</p>
            <p className="font-bold text-red-400">{(eda?.churn_rate * 100)?.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-400">Churned</p>
            <p className="font-bold">{eda?.churned?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-slate-400">Retained</p>
            <p className="font-bold text-emerald-400">{eda?.retained?.toLocaleString()}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mt-5">
          <AuthImage src={api.reportImage("eda_overview.png")} className="rounded-lg w-full border border-slate-700" alt="EDA overview" />
          <AuthImage src={api.reportImage("eda_correlation.png")} className="rounded-lg w-full border border-slate-700" alt="Correlation matrix" />
          <AuthImage src={api.reportImage("eda_tenure_curve.png")} className="rounded-lg w-full border border-slate-700" alt="Tenure curve" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-4 w-4 text-slate-500" />
            <h2 className="font-bold">Users</h2>
          </div>
          <div className="space-y-2">
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2">
                <div>
                  <p className="text-sm font-semibold">{u.username}</p>
                  <p className="text-[11px] text-slate-400">{u.email}</p>
                </div>
                <span className="text-xs uppercase px-2 py-1 rounded bg-indigo-500/15 text-indigo-300">{u.role}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <ShieldPlus className="h-4 w-4 text-slate-500" />
            <h2 className="font-bold">Create User</h2>
          </div>
          {msg && <p className="text-sm text-emerald-400 mb-3">{msg}</p>}
          <form onSubmit={createUser} className="space-y-3">
            <input
              className="input"
              placeholder="Username"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              required
            />
            <input
              type="email"
              className="input"
              placeholder="Email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              required
            />
            <input
              type="password"
              className="input"
              placeholder="Password (min 6 chars)"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              required
              minLength={6}
            />
            <select
              className="input"
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
            >
              <option value="viewer">viewer</option>
              <option value="analyst">analyst</option>
              <option value="admin">admin</option>
            </select>
            <button className="btn-primary w-full">Create User</button>
          </form>
        </div>
      </div>
    </div>
  );
}

function Row({ k, v }) {
  return (
    <div className="flex justify-between border-b border-slate-700/50 pb-1.5">
      <dt className="text-slate-400">{k}</dt>
      <dd className="font-semibold">{v ?? "—"}</dd>
    </div>
  );
}

function BarChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
        <Bar dataKey="Churn rate" fill="#ef4444" radius={[4, 4, 0, 0]} />
      </LineChart>
    </ResponsiveContainer>
  );
}
