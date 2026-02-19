import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  ShoppingBag, Users, Pill, AlertTriangle,
  TrendingUp, Calendar, ChevronRight, IndianRupee, Clock
} from "lucide-react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
        {sub && <p className="text-xs text-slate-400">{sub}</p>}
      </div>
    </div>
  );
}

function statusBadge(s) {
  const map = { pending: "badge-amber", confirmed: "badge-blue", completed: "badge-green", cancelled: "badge-red" };
  return <span className={map[s] || "badge-slate"}>{s}</span>;
}

// ── Customer Dashboard ─────────────────────────────────────
function CustomerDashboard({ user }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getMyStats(), api.getMyOrders()])
      .then(([s, o]) => { setStats(s.data); setOrders(o.data.slice(0, 20)); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          Good {new Date().getHours() < 12 ? "morning" : "afternoon"}, {user?.name?.split(" ")[0]} 👋
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">Here are your orders.</p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard icon={ShoppingBag}  label="Total Orders"   value={stats.total_orders}  color="bg-blue-500" />
          <StatCard icon={Clock}        label="Pending"        value={stats.pending_orders} color="bg-amber-500" />
          <StatCard icon={IndianRupee}  label="Total Spent"    value={`₹${(stats.total_spent || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`} color="bg-emerald-500" />
        </div>
      )}

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">My Orders</h2>
          <span className="text-xs text-slate-400">{orders.length} orders</span>
        </div>
        <OrdersTable orders={orders} navigate={navigate} />
      </div>
    </div>
  );
}

// ── Shopkeeper / Admin Dashboard ──────────────────────────
function ShopDashboard({ user }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getDashboardStats(), api.getOrders()])
      .then(([s, o]) => { setStats(s.data); setOrders(o.data.slice(0, 20)); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          Good {new Date().getHours() < 12 ? "morning" : "afternoon"}, {user?.name?.split(" ")[0]} 👋
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">Here's what's happening today.</p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
          <StatCard icon={ShoppingBag}   label="Total Orders"    value={stats.total_orders}         color="bg-blue-500"    sub={`${stats.today_orders} today`} />
          <StatCard icon={Users}         label="Customers"       value={stats.total_customers}       color="bg-emerald-500" />
          <StatCard icon={Pill}          label="Medicines"       value={stats.total_medicines}        color="bg-violet-500" />
          <StatCard icon={AlertTriangle} label="Low Stock"       value={stats.low_stock_medicines}    color="bg-amber-500"   sub="need reorder" />
          <StatCard icon={IndianRupee}   label="Total Revenue"   value={`₹${(stats.total_revenue || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`} color="bg-rose-500" />
          <StatCard icon={Calendar}      label="Today's Orders"  value={stats.today_orders}           color="bg-sky-500" />
        </div>
      )}

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">Recent Orders</h2>
          <span className="text-xs text-slate-400">{orders.length} orders</span>
        </div>
        <OrdersTable orders={orders} navigate={navigate} />
      </div>
    </div>
  );
}

function OrdersTable({ orders, navigate }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <th className="px-5 py-3 text-left">Order ID</th>
            <th className="px-5 py-3 text-left">Customer</th>
            <th className="px-5 py-3 text-left">Date</th>
            <th className="px-5 py-3 text-left">Status</th>
            <th className="px-5 py-3 text-right">Amount</th>
            <th className="px-5 py-3 text-center">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {orders.length === 0 && (
            <tr>
              <td colSpan={6} className="px-5 py-10 text-center text-slate-400">No orders yet.</td>
            </tr>
          )}
          {orders.map((o) => (
            <tr key={o.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-5 py-3 font-mono font-medium text-blue-700">{o.order_number}</td>
              <td className="px-5 py-3 text-slate-700">{o.customer?.name || "—"}</td>
              <td className="px-5 py-3 text-slate-500">
                {new Date(o.order_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "2-digit" })}
              </td>
              <td className="px-5 py-3">{statusBadge(o.status)}</td>
              <td className="px-5 py-3 text-right font-semibold text-slate-800">
                ₹{(o.final_amount || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
              </td>
              <td className="px-5 py-3 text-center">
                <button
                  onClick={() => navigate(`/orders/${o.id}`)}
                  className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-xs font-medium"
                >
                  View <ChevronRight size={14} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Spinner() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const role = user?.role || "customer";

  if (role === "customer") return <CustomerDashboard user={user} />;
  return <ShopDashboard user={user} />;
}
