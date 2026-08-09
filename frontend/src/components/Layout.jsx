import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity,
  BarChart3,
  LayoutDashboard,
  LogOut,
  Search,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import { useAuth } from "../auth/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/search", label: "Customer Search", icon: Search },
  { to: "/analyze", label: "Analyze", icon: Sparkles },
  { to: "/admin", label: "Admin", icon: BarChart3, adminOnly: true },
];

export default function Layout() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 30000);
    return () => clearInterval(id);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-60 shrink-0 bg-slate-900/90 border-r border-slate-800 flex flex-col sticky top-0 h-screen">
        <div className="p-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-extrabold text-lg leading-none tracking-tight">
                Churn<span className="text-indigo-400">IQ</span>
              </h1>
              <p className="text-[11px] text-slate-400 mt-1">Churn Intelligence</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems
            .filter((i) => !i.adminOnly || isAdmin)
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`
                }
              >
                <item.icon className="h-4.5 w-4.5 h-[18px] w-[18px]" />
                {item.label}
              </NavLink>
            ))}
        </nav>

        <div className="p-4 border-t border-slate-800 space-y-3">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-slate-700 flex items-center justify-center">
              <Users className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold truncate">{user?.username}</p>
              <div className="flex items-center gap-1 text-[11px] text-indigo-300 capitalize">
                <ShieldCheck className="h-3 w-3" />
                {user?.role}
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="ml-auto p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-red-400"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
          <p className="text-[10px] text-slate-500">
            {time.toLocaleString()}
          </p>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
