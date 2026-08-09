import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import { api } from "../api/client";
import RiskBadge from "../components/RiskBadge";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();

  const runSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    try {
      const data = await api.searchCustomers(query, 50);
      setResults(data.customers);
      setSearched(true);
    } catch {
      setResults([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight">Customer Search</h1>
        <p className="text-sm text-slate-400">Find customers by ID, contract, or payment method</p>
      </header>

      <form onSubmit={runSearch} className="flex gap-3 max-w-2xl">
        <div className="relative flex-1">
          <SearchIcon className="h-4 w-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            className="input pl-9"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search customer ID, e.g. 9017c0b5…"
          />
        </div>
        <button className="btn-primary" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {searched && (
        <p className="text-sm text-slate-400">
          {results?.length || 0} customer{results?.length === 1 ? "" : "s"} found
        </p>
      )}

      {results?.length > 0 && (
        <div className="card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/70">
                <tr className="text-left text-xs uppercase tracking-wider text-slate-400">
                  <th className="px-4 py-3">Customer ID</th>
                  <th className="px-4 py-3">Tenure</th>
                  <th className="px-4 py-3">Contract</th>
                  <th className="px-4 py-3">Internet</th>
                  <th className="px-4 py-3">Monthly</th>
                  <th className="px-4 py-3">Payment</th>
                  <th className="px-4 py-3">Risk</th>
                  <th className="px-4 py-3">Label</th>
                </tr>
              </thead>
              <tbody>
                {results.map((c) => (
                  <tr
                    key={c.customer_id}
                    onClick={() => navigate(`/customers/${c.customer_id}`)}
                    className="border-t border-slate-700/50 hover:bg-slate-700/40 cursor-pointer"
                  >
                    <td className="px-4 py-3 font-semibold">{c.customer_id}</td>
                    <td className="px-4 py-3">{c.tenure} mo</td>
                    <td className="px-4 py-3">{c.contract}</td>
                    <td className="px-4 py-3">{c.internet_service}</td>
                    <td className="px-4 py-3">${c.monthly_charges?.toFixed(2)}</td>
                    <td className="px-4 py-3">{c.payment_method}</td>
                    <td className="px-4 py-3">
                      {c.risk ? <RiskBadge category={c.risk.category} probability={c.risk.probability} /> : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          c.churn_label === "Yes"
                            ? "bg-red-500/15 text-red-400"
                            : "bg-emerald-500/15 text-emerald-400"
                        }`}
                      >
                        {c.churn_label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {searched && !loading && results?.length === 0 && (
        <div className="card text-center py-10 text-slate-400">
          <Sparkles className="h-8 w-8 mx-auto mb-3 opacity-50" />
          <p>No customers matched your query.</p>
        </div>
      )}
    </div>
  );
}
