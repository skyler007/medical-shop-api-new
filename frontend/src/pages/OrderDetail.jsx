import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Package, User, Phone, Calendar, Printer } from "lucide-react";
import { api } from "../api/client";

function statusBadge(s) {
  const map = {
    pending: "badge-amber",
    confirmed: "badge-blue",
    completed: "badge-green",
    cancelled: "badge-red",
  };
  return <span className={map[s] || "badge-slate"}>{s}</span>;
}

export default function OrderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getOrder(id)
      .then((r) => setOrder(r.data))
      .catch(() => setError("Order not found"))
      .finally(() => setLoading(false));
  }, [id]);

/*  const handlePrint = async () => {
  if (!order?.id) {
    alert("Order not found.");
    return;
  }

  try {
    const response = await api.downloadInvoice(order.id);

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${order.order_number}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (err) {
    console.log("Download error:", err.response);
    alert("Failed to download invoice.");
  }
}; */

const handlePrint = () => {
  const token = localStorage.getItem("token");

  if (!order?.id) return;

  const url = `http://54.204.152.20/api/invoices/${order.id}/download`;

  // If your backend requires token:
  window.open(url, "_blank");
};



  if (loading)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );

  if (error || !order)
    return (
      <div className="p-6">
        <div className="card text-center py-12 text-slate-400">
          {error || "Order not found"}
        </div>
      </div>
    );

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} className="text-slate-600" />
        </button>

        <div>
          <h1 className="text-xl font-bold text-slate-800 font-mono">
            {order.order_number}
          </h1>
          <p className="text-sm text-slate-500">Order Details</p>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {statusBadge(order.status)}

          <button
            onClick={handlePrint}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Printer size={15} /> Print Invoice
          </button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card space-y-3">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2">
            <User size={16} /> Customer
          </h2>
          <p className="text-slate-800 font-medium">
            {order.customer?.name || "Walk-in Customer"}
          </p>
          {order.customer?.phone && (
            <p className="text-slate-500 text-sm flex items-center gap-1.5">
              <Phone size={13} /> {order.customer.phone}
            </p>
          )}
        </div>

        <div className="card space-y-3">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2">
            <Calendar size={16} /> Order Info
          </h2>
          <p className="text-sm text-slate-500">
            Placed on{" "}
            <span className="text-slate-700">
              {new Date(order.order_date).toLocaleString("en-IN")}
            </span>
          </p>
        </div>

        <div className="card space-y-2">
          <h2 className="font-semibold text-slate-700">Summary</h2>
          <div className="flex justify-between text-sm">
            <span>Subtotal</span>
            <span>₹{order.total_amount?.toFixed(2) || "0.00"}</span>
          </div>
          <div className="flex justify-between font-bold border-t pt-2">
            <span>Total</span>
            <span className="text-blue-700">
              ₹{order.final_amount?.toFixed(2) || "0.00"}
            </span>
          </div>
        </div>
      </div>

      {/* Items */}
      <div className="card p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs uppercase">
              <th className="px-5 py-3 text-left">#</th>
              <th className="px-5 py-3 text-left">Medicine</th>
              <th className="px-5 py-3 text-center">Qty</th>
              <th className="px-5 py-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {order.order_items?.map((item, i) => (
              <tr key={item.id}>
                <td className="px-5 py-3">{i + 1}</td>
                <td className="px-5 py-3">
                  {item.medicine?.name}
                </td>
                <td className="px-5 py-3 text-center">
                  {item.quantity}
                </td>
                <td className="px-5 py-3 text-right">
                  ₹{item.total_price?.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
