const API_URL = import.meta.env.VITE_API_URL || "/api";

function getToken() {
  return localStorage.getItem("churniq_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    localStorage.removeItem("churniq_token");
    localStorage.removeItem("churniq_user");
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      detail = JSON.parse(text).detail || text;
    } catch {
      /* keep text */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  login: (username, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  me: () => request("/auth/me"),
  health: () => request("/health"),
  modelInfo: () => request("/model/info"),
  predict: (payload) =>
    request("/predict", { method: "POST", body: JSON.stringify(payload) }),
  predictions: (limit = 20) => request(`/predictions?limit=${limit}`),
  prediction: (id) => request(`/predictions/${id}`),
  searchCustomers: (q = "", limit = 25) =>
    request(`/customers/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  customer: (id) => request(`/customers/${encodeURIComponent(id)}`),
  adminStats: () => request("/admin/stats"),
  adminModel: () => request("/admin/model"),
  adminEda: () => request("/admin/eda"),
  adminUsers: () => request("/admin/users"),
  createUser: (body) =>
    request("/admin/users", { method: "POST", body: JSON.stringify(body) }),
  predictionSummary: (days = 30) =>
    request(`/admin/prediction-summary?days=${days}`),
  reportImage: (name) => `${API_URL}/admin/reports/${encodeURIComponent(name)}`,
};
