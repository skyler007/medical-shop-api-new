import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Package, Download, User, Phone, Calendar } from "lucide-react";
import { api } from "../api/client";

function statusBadge(s) {
  const map = { pending: "badge-amber", confirmed: "badge-blue", completed: "badge-green", cancelled: "badge-red" };
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

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !order) return (
    <div className="p-6">
      <div className="card text-center py-12 text-slate-400">{error || "Order not found"}</div>
    </div>
  );

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <ArrowLeft size={20} className="text-slate-600" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-slate-800 font-mono">{order.order_number}</h1>
          <p className="text-sm text-slate-500">Order Details</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {statusBadge(order.status)}
          {order.invoice && (
            <a
              href={api.downloadInvoice(order.invoice.id)}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary flex items-center gap-2 text-sm"
            >
              <Download size={15} /> Invoice PDF
            </a>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Customer Info */}
        <div className="card space-y-3">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2">
            <User size={16} /> Customer
          </h2>
          <p className="text-slate-800 font-medium">{order.customer?.name}</p>
          {order.customer?.phone && (
            <p className="text-slate-500 text-sm flex items-center gap-1.5">
              <Phone size={13} /> {order.customer.phone}
            </p>
          )}
        </div>

        {/* Order Info */}
        <div className="card space-y-3">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2">
            <Calendar size={16} /> Order Info
          </h2>
          <p className="text-sm text-slate-500">
            Placed on <span className="text-slate-700">{new Date(order.order_date).toLocaleString("en-IN")}</span>
          </p>
          <p className="text-sm text-slate-500">
            Source: <span className="text-slate-700 capitalize">{order.order_source}</span>
          </p>
          {order.notes && <p className="text-sm text-slate-500">Note: {order.notes}</p>}
        </div>

        {/* Totals */}
        <div className="card space-y-2">
          <h2 className="font-semibold text-slate-700">Summary</h2>
          <div className="flex justify-between text-sm"><span className="text-slate-500">Subtotal</span><span>₹{order.total_amount?.toFixed(2)}</span></div>
          {order.discount_amount > 0 && <div className="flex justify-between text-sm text-emerald-600"><span>Discount</span><span>-₹{order.discount_amount?.toFixed(2)}</span></div>}
          {order.tax_amount > 0 && <div className="flex justify-between text-sm"><span className="text-slate-500">Tax</span><span>₹{order.tax_amount?.toFixed(2)}</span></div>}
          <div className="flex justify-between font-bold text-base border-t border-slate-100 pt-2">
            <span>Total</span><span className="text-blue-700">₹{order.final_amount?.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Items Table */}
      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
          <Package size={16} className="text-slate-500" />
          <h2 className="font-semibold text-slate-800">Medicines Ordered</h2>
          <span className="ml-auto text-xs text-slate-400">{order.order_items?.length} items</span>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
              <th className="px-5 py-3 text-left">#</th>
              <th className="px-5 py-3 text-left">Medicine</th>
              <th className="px-5 py-3 text-left">Packaging</th>
              <th className="px-5 py-3 text-center">Qty</th>
              <th className="px-5 py-3 text-right">Unit Price</th>
              <th className="px-5 py-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {order.order_items?.map((item, i) => (
              <tr key={item.id} className="hover:bg-slate-50">
                <td className="px-5 py-3 text-slate-400">{i + 1}</td>
                <td className="px-5 py-3">
                  <p className="font-medium text-slate-800">{item.medicine?.name || `Medicine #${item.medicine_id}`}</p>
                  {item.medicine?.name_hindi && <p className="text-xs text-slate-400">{item.medicine.name_hindi}</p>}
                </td>
                <td className="px-5 py-3 capitalize text-slate-600">{item.packaging_type}</td>
                <td className="px-5 py-3 text-center font-medium">{item.quantity}</td>
                <td className="px-5 py-3 text-right text-slate-600">₹{item.price_per_unit?.toFixed(2)}</td>
                <td className="px-5 py-3 text-right font-semibold text-slate-800">₹{item.total_price?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
