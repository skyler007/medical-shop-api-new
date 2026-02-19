import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShoppingCart, Trash2, Plus, Minus, AlertCircle, CheckCircle } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

const PACKAGING = ["strip", "bottle", "box", "loose", "tube", "vial"];

export default function Cart() {
  const { items, removeItem, updateQuantity, clearCart, total } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: user?.name || "", phone: "", address: "" });
  const [placing, setPlacing] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState("");

  const handleQty = (item, delta) => {
    const newQty = item.quantity + delta;
    if (newQty < 1) return;
    if (newQty > item.stock_quantity) return;
    updateQuantity(item.medicine_id, item.packaging_type, newQty);
  };

  const handlePlaceOrder = async () => {
    if (!form.name || !form.phone) { setError("Please fill in your name and phone."); return; }
    setError("");
    setPlacing(true);
    try {
      const payload = {
        customer_name: form.name,
        customer_phone: form.phone,
        customer_address: form.address || null,
        items: items.map((i) => ({
          medicine_id: i.medicine_id,
          quantity: i.quantity,
          packaging_type: i.packaging_type,
        })),
        order_source: "online",
        language_used: "english",
      };
      const res = await api.createOrder(payload);
      setSuccess(res.data);
      clearCart();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to place order. Please try again.");
    } finally {
      setPlacing(false);
    }
  };

  if (success) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="card max-w-md w-full text-center space-y-4">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle size={32} className="text-emerald-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-800">Order Placed!</h2>
          <p className="text-slate-500">Your order has been confirmed.</p>
          <div className="bg-slate-50 rounded-lg p-4 text-sm text-left space-y-1">
            <div className="flex justify-between"><span className="text-slate-500">Order #</span><span className="font-mono font-medium text-blue-700">{success.order_number}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Total</span><span className="font-bold">₹{success.final_amount?.toFixed(2)}</span></div>
          </div>
          <div className="flex gap-3">
            <button onClick={() => navigate(`/orders/${success.id}`)} className="btn-primary flex-1">View Order</button>
            <button onClick={() => navigate("/")} className="btn-secondary flex-1">Dashboard</button>
          </div>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <ShoppingCart size={48} className="text-slate-200 mx-auto" />
          <h2 className="text-lg font-semibold text-slate-600">Your cart is empty</h2>
          <p className="text-sm text-slate-400">Add medicines from the chat or manual order page.</p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => navigate("/order/chat")} className="btn-primary">Chat Order</button>
            <button onClick={() => navigate("/order/manual")} className="btn-secondary">Manual Order</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Your Cart</h1>
        <button onClick={clearCart} className="text-sm text-red-500 hover:text-red-700 flex items-center gap-1">
          <Trash2 size={14} /> Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Items */}
        <div className="lg:col-span-2 space-y-3">
          {items.map((item) => (
            <div key={`${item.medicine_id}-${item.packaging_type}`} className="card flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-800">{item.medicine_name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <select
                    value={item.packaging_type}
                    onChange={(e) => { removeItem(item.medicine_id, item.packaging_type); }}
                    className="text-xs border border-slate-200 rounded px-2 py-1 bg-slate-50"
                  >
                    {PACKAGING.map((p) => <option key={p}>{p}</option>)}
                  </select>
                  <span className="text-xs text-slate-400">₹{item.price_per_unit}/unit</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handleQty(item, -1)} className="w-7 h-7 rounded-full border border-slate-200 flex items-center justify-center hover:bg-slate-50">
                  <Minus size={12} />
                </button>
                <span className="w-8 text-center font-medium text-slate-800">{item.quantity}</span>
                <button onClick={() => handleQty(item, 1)} disabled={item.quantity >= item.stock_quantity}
                  className="w-7 h-7 rounded-full border border-slate-200 flex items-center justify-center hover:bg-slate-50 disabled:opacity-40">
                  <Plus size={12} />
                </button>
              </div>
              <p className="w-24 text-right font-semibold text-slate-800">₹{item.total_price.toFixed(2)}</p>
              <button onClick={() => removeItem(item.medicine_id, item.packaging_type)} className="text-slate-300 hover:text-red-500 transition-colors">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>

        {/* Checkout */}
        <div className="space-y-4">
          <div className="card space-y-3">
            <h2 className="font-semibold text-slate-800">Order Total</h2>
            <div className="flex justify-between text-sm text-slate-500"><span>Subtotal ({items.length} items)</span><span>₹{total.toFixed(2)}</span></div>
            <div className="flex justify-between font-bold text-base border-t border-slate-100 pt-2">
              <span>Total</span><span className="text-blue-700">₹{total.toFixed(2)}</span>
            </div>
          </div>

          <div className="card space-y-3">
            <h2 className="font-semibold text-slate-800">Customer Info</h2>
            {error && (
              <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-2 rounded-lg">
                <AlertCircle size={14} /> {error}
              </div>
            )}
            <input className="input-field" placeholder="Full Name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="input-field" placeholder="Phone *" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <input className="input-field" placeholder="Address (optional)" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            <button onClick={handlePlaceOrder} disabled={placing} className="btn-primary w-full py-2.5">
              {placing ? "Placing Order…" : `Place Order · ₹${total.toFixed(2)}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
