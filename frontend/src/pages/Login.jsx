import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity, KeyRound, User } from "lucide-react";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight">
              Churn<span className="text-indigo-400">IQ</span>
            </h1>
            <p className="text-sm text-slate-400">Enterprise Churn Prediction Platform</p>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-bold mb-1">Sign in</h2>
          <p className="text-sm text-slate-400 mb-5">Use your platform credentials to continue.</p>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Username</label>
              <div className="relative">
                <User className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  className="input pl-9"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  autoFocus
                  required
                />
              </div>
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <KeyRound className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  className="input pl-9"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <button className="btn-primary w-full" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="text-xs text-slate-500 mt-5 text-center">
            Default credentials: <code className="text-slate-300">admin / admin123</code>
          </p>
        </div>
      </div>
    </div>
  );
}
