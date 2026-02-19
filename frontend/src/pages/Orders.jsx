import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronRight, Search } from "lucide-react";
import { api } from "../api/client";

const STATUS_OPTIONS = ["all", "pending", "confirmed", "completed", "cancelled"];

function statusBadge(s) {
  const map = { pending: "badge-amber", confirmed: "badge-blue", completed: "badge-green", cancelled: "badge-red" };
  return <span className={map[s] || "badge-slate"}>{s}</span>;
}

export default function Orders() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [status, setStatus] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOrders()
      .then((r) => { setOrders(r.data); setFiltered(r.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let result = orders;
    if (status !== "all") result = result.filter((o) => o.status === status);
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (o) => o.order_number.toLowerCase().includes(q) || o.customer?.name?.toLowerCase().includes(q)
      );
    }
    setFiltered(result);
  }, [status, search, orders]);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-6 space-y-5">
      <h1 className="text-2xl font-bold text-slate-800">All Orders</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input-field pl-8 w-52"
            placeholder="Search order / customer…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {STATUS_OPTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                status === s ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <th className="px-5 py-3 text-left">Order #</th>
                <th className="px-5 py-3 text-left">Customer</th>
                <th className="px-5 py-3 text-left">Date</th>
                <th className="px-5 py-3 text-left">Status</th>
                <th className="px-5 py-3 text-left">Source</th>
                <th className="px-5 py-3 text-right">Amount</th>
                <th className="px-5 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-5 py-10 text-center text-slate-400">No orders found.</td></tr>
              )}
              {filtered.map((o) => (
                <tr key={o.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3 font-mono font-medium text-blue-700">{o.order_number}</td>
                  <td className="px-5 py-3 text-slate-700">{o.customer?.name || "—"}</td>
                  <td className="px-5 py-3 text-slate-500">
                    {new Date(o.order_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "2-digit" })}
                  </td>
                  <td className="px-5 py-3">{statusBadge(o.status)}</td>
                  <td className="px-5 py-3 text-slate-500 capitalize">{o.order_source}</td>
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
        <div className="px-5 py-3 border-t border-slate-100 text-xs text-slate-400">
          Showing {filtered.length} of {orders.length} orders
        </div>
      </div>
    </div>
  );
}
