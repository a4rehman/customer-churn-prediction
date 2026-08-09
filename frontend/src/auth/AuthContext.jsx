import { createContext, useContext, useCallback, useMemo, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("churniq_user") || "null");
    } catch {
      return null;
    }
  });

  const login = useCallback(async (username, password) => {
    const data = await api.login(username, password);
    const profile = { username: data.username, role: data.role };
    localStorage.setItem("churniq_token", data.access_token);
    localStorage.setItem("churniq_user", JSON.stringify(profile));
    setUser(profile);
    return profile;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("churniq_token");
    localStorage.removeItem("churniq_user");
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, login, logout, isAdmin: user?.role === "admin" }),
    [user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
