import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { History, Wand2 } from "lucide-react";
import { api } from "../api/client";
import ProbabilityGauge from "../components/ProbabilityGauge";
import RiskBadge from "../components/RiskBadge";
import ShapBar from "../components/ShapBar";
import Recommendations from "../components/Recommendations";

const DEFAULT_FORM = {
  customer_id: "",
  gender: "Male",
  SeniorCitizen: 0,
  Partner: "No",
  Dependents: "No",
  tenure: 12,
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "DSL",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "No",
  PaymentMethod: "Electronic check",
  MonthlyCharges: 60,
  TotalCharges: 720,
};

const SNAKE_TO_CAMEL = {
  gender: "gender",
  senior_citizen: "SeniorCitizen",
  partner: "Partner",
  dependents: "Dependents",
  tenure: "tenure",
  phone_service: "PhoneService",
  multiple_lines: "MultipleLines",
  internet_service: "InternetService",
  online_security: "OnlineSecurity",
  online_backup: "OnlineBackup",
  device_protection: "DeviceProtection",
  tech_support: "TechSupport",
  streaming_tv: "StreamingTV",
  streaming_movies: "StreamingMovies",
  contract: "Contract",
  paperless_billing: "PaperlessBilling",
  payment_method: "PaymentMethod",
  monthly_charges: "MonthlyCharges",
  total_charges: "TotalCharges",
};

export default function CustomerDetail() {
  const { customerId } = useParams();
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const isAnalyze = !customerId;

  useEffect(() => {
    if (!customerId) return;
    (async () => {
      try {
        const c = await api.customer(customerId);
        const mapped = {};
        for (const [snake, camel] of Object.entries(SNAKE_TO_CAMEL)) {
          mapped[camel] = c[snake];
        }
        setForm({ ...DEFAULT_FORM, ...mapped });
        await runPredict({ ...DEFAULT_FORM, ...mapped });
      } catch (err) {
        setError(err.message);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [customerId]);

  const runPredict = async (overrideForm) => {
    setLoading(true);
    setError("");
    try {
      const payload = { ...(overrideForm || form) };
      const res = await api.predict(payload);
      setResult(res);
      const preds = await api.predictions(50);
      setHistory(preds.filter((p) => p.customer_id === (payload.customer_id || res.customer_id)).slice(0, 10));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const selectOptions = useMemo(
    () => ({
      gender: ["Male", "Female"],
      Partner: ["Yes", "No"],
      Dependents: ["Yes", "No"],
      PhoneService: ["Yes", "No"],
      MultipleLines: ["Yes", "No"],
      InternetService: ["Fiber optic", "DSL", "No"],
      OnlineSecurity: ["Yes", "No"],
      OnlineBackup: ["Yes", "No"],
      DeviceProtection: ["Yes", "No"],
      TechSupport: ["Yes", "No"],
      StreamingTV: ["Yes", "No"],
      StreamingMovies: ["Yes", "No"],
      Contract: ["Month-to-month", "One year", "Two year"],
      PaperlessBilling: ["Yes", "No"],
      PaymentMethod: ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
    }),
    []
  );

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight">
          {isAnalyze ? "Customer Analyzer" : `Customer ${customerId}`}
        </h1>
        <p className="text-sm text-slate-400">
          {isAnalyze
            ? "Build a customer profile and get a live churn prediction"
            : "Live risk profile, model explanations, and retention actions"}
        </p>
        {error && (
          <p className="text-sm text-red-400 mt-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">{error}</p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Wand2 className="h-4 w-4 text-indigo-400" />
            <h2 className="font-bold">Customer Profile</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <Field label="Customer ID" value={form.customer_id} onChange={(v) => set("customer_id", v)} placeholder="AUTO" />
            <Field label="Gender" value={form.gender} onChange={(v) => set("gender", v)} options={selectOptions.gender} />
            <Field label="Senior Citizen" value={form.SeniorCitizen} onChange={(v) => set("SeniorCitizen", Number(v))} options={[0, 1]} />
            <Field label="Partner" value={form.Partner} onChange={(v) => set("Partner", v)} options={selectOptions.Partner} />
            <Field label="Dependents" value={form.Dependents} onChange={(v) => set("Dependents", v)} options={selectOptions.Dependents} />
            <Field label="Tenure (months)" value={form.tenure} onChange={(v) => set("tenure", Number(v))} type="number" />
            <Field label="Phone Service" value={form.PhoneService} onChange={(v) => set("PhoneService", v)} options={selectOptions.PhoneService} />
            <Field label="Multiple Lines" value={form.MultipleLines} onChange={(v) => set("MultipleLines", v)} options={selectOptions.MultipleLines} />
            <Field label="Internet Service" value={form.InternetService} onChange={(v) => set("InternetService", v)} options={selectOptions.InternetService} />
            <Field label="Online Security" value={form.OnlineSecurity} onChange={(v) => set("OnlineSecurity", v)} options={selectOptions.OnlineSecurity} />
            <Field label="Online Backup" value={form.OnlineBackup} onChange={(v) => set("OnlineBackup", v)} options={selectOptions.OnlineBackup} />
            <Field label="Device Protection" value={form.DeviceProtection} onChange={(v) => set("DeviceProtection", v)} options={selectOptions.DeviceProtection} />
            <Field label="Tech Support" value={form.TechSupport} onChange={(v) => set("TechSupport", v)} options={selectOptions.TechSupport} />
            <Field label="Streaming TV" value={form.StreamingTV} onChange={(v) => set("StreamingTV", v)} options={selectOptions.StreamingTV} />
            <Field label="Streaming Movies" value={form.StreamingMovies} onChange={(v) => set("StreamingMovies", v)} options={selectOptions.StreamingMovies} />
            <Field label="Contract" value={form.Contract} onChange={(v) => set("Contract", v)} options={selectOptions.Contract} />
            <Field label="Paperless Billing" value={form.PaperlessBilling} onChange={(v) => set("PaperlessBilling", v)} options={selectOptions.PaperlessBilling} />
            <Field label="Payment Method" value={form.PaymentMethod} onChange={(v) => set("PaymentMethod", v)} options={selectOptions.PaymentMethod} />
            <Field label="Monthly Charges ($)" value={form.MonthlyCharges} onChange={(v) => set("MonthlyCharges", Number(v))} type="number" />
            <Field label="Total Charges ($)" value={form.TotalCharges} onChange={(v) => set("TotalCharges", Number(v))} type="number" />
          </div>
          <button className="btn-primary mt-5" onClick={() => runPredict()} disabled={loading}>
            {loading ? "Predicting…" : "Run Prediction"}
          </button>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h2 className="font-bold mb-3">Churn Risk</h2>
            <ProbabilityGauge probability={result?.probability} />
            {result && (
              <div className="flex flex-col items-center gap-2 mt-3">
                <RiskBadge category={result.risk_category} probability={result.probability} />
                <p className="text-xs text-slate-400">
                  Model prediction: <span className="font-semibold text-slate-200">{result.churn_prediction}</span> ·
                  v{result.model_version}
                </p>
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="font-bold mb-4">What drives this prediction</h2>
            <ShapBar contributions={result?.top_contributors} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-bold mb-4">Recommended Actions</h2>
          <Recommendations recommendations={result?.recommendations} />
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <History className="h-4 w-4 text-slate-500" />
            <h2 className="font-bold">Prediction History</h2>
          </div>
          {history.length === 0 ? (
            <p className="text-sm text-slate-400">No prior predictions for this customer.</p>
          ) : (
            <div className="space-y-2">
              {history.map((p) => (
                <div key={p.id} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2">
                  <div>
                    <p className="text-sm font-medium">{new Date(p.predicted_at).toLocaleString()}</p>
                    <p className="text-[11px] text-slate-400">{p.model_version}</p>
                  </div>
                  <RiskBadge category={p.risk_category} probability={p.probability} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, options, type = "text", placeholder }) {
  return (
    <div>
      <label className="label">{label}</label>
      {options ? (
        <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
          {options.map((o) => (
            <option key={String(o)} value={o}>
              {o}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          className="input"
          value={value ?? ""}
          placeholder={placeholder}
          onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
          step="any"
        />
      )}
    </div>
  );
}
