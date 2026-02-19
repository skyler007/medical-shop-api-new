import axios from "axios";

// In dev, Vite proxies /api → localhost:8000. In prod, set to your backend URL.
const BASE_URL = import.meta.env.VITE_API_URL || "";

const client = axios.create({ baseURL: BASE_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const api = {
  // Auth
  register: (data) => client.post("/api/auth/register", data),
  login: (data) => client.post("/api/auth/login", data),
  getMe: () => client.get("/api/auth/me"),
  updateProfile: (data) => client.put("/api/auth/profile", data),
  changePassword: (data) => client.put("/api/auth/change-password", data),

  // Medicines
  getMedicines: (skip = 0, limit = 100) => client.get(`/api/medicines?skip=${skip}&limit=${limit}`),
  searchMedicines: (query, limit = 10) => client.post("/api/medicines/search", { query, limit }),
  createMedicine: (data) => client.post("/api/medicines", data),
  updateMedicine: (id, data) => client.put(`/api/medicines/${id}`, data),
  deleteMedicine: (id) => client.delete(`/api/medicines/${id}`),
  getMedicinesByName: (name) => client.get(`/api/medicines/by-name`, { params: { name } }),

  // Orders
  getOrders: () => client.get("/api/orders?limit=200"),
  getMyOrders: () => client.get("/api/orders/my"),
  getOrder: (id) => client.get(`/api/orders/${id}`),
  createOrder: (data) => client.post("/api/orders", data),

  // Dashboard
  getDashboardStats: () => client.get("/api/dashboard/stats"),
  getMyStats: () => client.get("/api/dashboard/my-stats"),
  getLowStock: () => client.get("/api/dashboard/low-stock"),

  // Admin
  getUsers: () => client.get("/api/admin/users"),
  updateUserStatus: (id, is_active) => client.put(`/api/admin/users/${id}/status`, { is_active }),

  // Invoice
  downloadInvoice: (id) => `${BASE_URL || "http://localhost:8000"}/api/invoices/${id}/download`,
};

export default client;
