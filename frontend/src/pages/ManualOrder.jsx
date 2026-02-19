import { useState, useRef, useCallback } from "react";
import { Plus, Trash2, Save, ShoppingBag, AlertTriangle, CheckCircle, Search, ChevronDown } from "lucide-react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const emptyRow = () => ({
  id: Date.now() + Math.random(),
  medicine: null,
  selectedMedicineId: null,
  medicineName: "",
  suggestions: [],
  showSuggestions: false,
  packaging: "",
  packagingOptions: [],
  quantity: 1,
  loadingSuggestions: false,
});

function StockWarningModal({ item, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
            <AlertTriangle size={20} className="text-amber-600" />
          </div>
          <h3 className="font-semibold text-slate-800">Insufficient Stock</h3>
        </div>
        <p className="text-slate-600 text-sm">
          You requested <strong>{item.quantity}</strong> units of <strong>{item.medicine?.name}</strong>,
          but only <strong>{item.medicine?.stock_quantity}</strong> are available.
        </p>
        <p className="text-slate-500 text-sm">Please reduce the quantity.</p>
        <button onClick={onClose} className="btn-primary w-full">Got It</button>
      </div>
    </div>
  );
}

function SuccessModal({ order, onClose, onViewOrder }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 space-y-4">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle size={28} className="text-emerald-600" />
          </div>
          <h3 className="font-semibold text-slate-800 text-lg">Order Placed!</h3>
          <p className="text-slate-500 text-sm">Your order has been confirmed.</p>
        </div>
        <div className="bg-slate-50 rounded-xl p-4 text-sm space-y-1.5">
          <div className="flex justify-between"><span className="text-slate-500">Order #</span><span className="font-mono font-bold text-blue-700">{order.order_number}</span></div>
          <div className="flex justify-between"><span className="text-slate-500">Total</span><span className="font-bold">₹{order.final_amount?.toFixed(2)}</span></div>
          <div className="flex justify-between"><span className="text-slate-500">Status</span><span className="text-emerald-600 capitalize">{order.status}</span></div>
        </div>
        <div className="flex gap-3">
          <button onClick={onViewOrder} className="btn-primary flex-1">View Order</button>
          <button onClick={onClose} className="btn-secondary flex-1">New Order</button>
        </div>
      </div>
    </div>
  );
}

export default function ManualOrder() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [rows, setRows] = useState([emptyRow()]);
  const [customer, setCustomer] = useState({ name: user?.name || "", phone: user?.phone || "", address: "" });
  const [stockWarning, setStockWarning] = useState(null);
  const [successOrder, setSuccessOrder] = useState(null);
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState("");
  const [draft, setDraft] = useState(null);
  const debounceTimers = useRef({});

  const searchMedicines = useCallback(async (rowId, query) => {
    if (query.length < 2) {
      setRows((r) => r.map((row) =>
        row.id === rowId ? { ...row, suggestions: [], showSuggestions: false, loadingSuggestions: false } : row
      ));
      return;
    }
    try {
      const res = await api.searchMedicines(query, 8);
      setRows((r) => r.map((row) =>
        row.id === rowId
          ? { ...row, suggestions: res.data.medicines, showSuggestions: true, loadingSuggestions: false }
          : row
      ));
    } catch {
      setRows((r) => r.map((row) => row.id === rowId ? { ...row, loadingSuggestions: false } : row));
    }
  }, []);

  const handleMedicineInput = (rowId, value) => {
    setRows((r) => r.map((row) =>
      row.id === rowId
        ? { ...row, medicineName: value, medicine: null, selectedMedicineId: null, packagingOptions: [], packaging: "", loadingSuggestions: value.length >= 2 }
        : row
    ));
    clearTimeout(debounceTimers.current[rowId]);
    debounceTimers.current[rowId] = setTimeout(() => searchMedicines(rowId, value), 300);
  };

  const selectMedicine = (rowId, medicine) => {
  setRows((r) =>
    r.map((row) =>
      row.id === rowId
        ? {
            ...row,
            medicine,
            medicineName: medicine.name,
            selectedMedicineId: medicine.id,
            packaging: medicine.default_packaging || "",
            packagingOptions: [], // disable dropdown logic
            suggestions: [],
            showSuggestions: false,
            loadingSuggestions: false,
          }
        : row
    )
  );
};



  const handlePackagingChange = (rowId, selectedOption) => {
    setRows((r) => r.map((row) => {
      if (row.id !== rowId) return row;
      return {
        ...row,
        packaging: selectedOption.packaging,
        selectedMedicineId: selectedOption.id,
        medicine: {
          ...row.medicine,
          id: selectedOption.id,
          stock_quantity: selectedOption.stock_quantity,
          price_per_unit: selectedOption.price_per_unit,
        },
      };
    }));
  };

  const handleQtyChange = (rowId, value) => {
    const qty = parseInt(value) || 1;
    setRows((r) => r.map((row) => {
      if (row.id !== rowId) return row;
      if (row.medicine && qty > row.medicine.stock_quantity) {
        setStockWarning({ ...row, quantity: qty });
        return row;
      }
      return { ...row, quantity: qty };
    }));
  };

  const addRow = () => setRows((r) => [...r, emptyRow()]);

  const removeRow = (rowId) => {
    if (rows.length === 1) { setRows([emptyRow()]); return; }
    setRows((r) => r.filter((row) => row.id !== rowId));
  };

  const validRows = rows.filter((r) => r.medicine && r.selectedMedicineId && r.quantity > 0);

  const estimateTotal = validRows.reduce((s, r) => s + (r.medicine.price_per_unit * r.quantity), 0);

  const handlePlaceOrder = async () => {
    if (!customer.name || !customer.phone) { setError("Customer name and phone are required."); return; }
    if (validRows.length === 0) { setError("Please add at least one medicine."); return; }
    setError("");
    setPlacing(true);
    try {
      const payload = {
        customer_name: customer.name,
        customer_phone: customer.phone,
        customer_address: customer.address || null,
        items: validRows.map((r) => ({
          medicine_id: r.selectedMedicineId,
          quantity: r.quantity,
          packaging_type: r.packaging,
        })),
        order_source: "walk-in",
        language_used: "english",
      };
      const res = await api.createOrder(payload);
      setSuccessOrder(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to place order.");
    } finally {
      setPlacing(false);
    }
  };

  const handleSaveDraft = () => {
    const d = {
      customer,
      rows: validRows.map((r) => ({
        name: r.medicine.name,
        packaging: r.packaging,
        qty: r.quantity,
        price: r.medicine.price_per_unit,
      })),
    };
    setDraft(d);
    localStorage.setItem("order_draft", JSON.stringify(d));
  };

  return (
    <div className="flex flex-col min-h-screen">
      {stockWarning && <StockWarningModal item={stockWarning} onClose={() => setStockWarning(null)} />}
      {successOrder && (
        <SuccessModal
          order={successOrder}
          onClose={() => {
            setSuccessOrder(null);
            setRows([emptyRow()]);
            setCustomer({ name: user?.name || "", phone: "", address: "" });
          }}
          onViewOrder={() => navigate(`/orders/${successOrder.id}`)}
        />
      )}

      {/* Header */}
      <div className="px-6 py-5 bg-white border-b border-slate-100">
        <h1 className="text-xl font-bold text-slate-800">New Manual Order</h1>
        <p className="text-sm text-slate-500 mt-0.5">Fill in customer details and add medicines</p>
      </div>

      <div className="flex-1 p-6 space-y-5">
        {/* Customer Details */}
        <div className="card grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Customer Name *</label>
            <input className="input-field" placeholder="Rajan Sharma" value={customer.name}
              onChange={(e) => setCustomer({ ...customer, name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Phone *</label>
            <input className="input-field" placeholder="+91 98765 43210" value={customer.phone}
              onChange={(e) => setCustomer({ ...customer, phone: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Address</label>
            <input className="input-field" placeholder="Optional" value={customer.address}
              onChange={(e) => setCustomer({ ...customer, address: e.target.value })} />
          </div>
        </div>

        {/* Medicines Table — overflow-visible so dropdowns escape */}
        <div className="card p-0 overflow-visible">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="font-semibold text-slate-800">Medicines</h2>
            <button onClick={addRow} className="btn-secondary flex items-center gap-1.5 text-sm py-1.5">
              <Plus size={15} /> Add Row
            </button>
          </div>

          <div className="overflow-visible">
            <table className="w-full text-sm" style={{ borderCollapse: "separate", borderSpacing: 0 }}>
              <thead>
                <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                  <th className="px-4 py-3 text-left w-10">#</th>
                  <th className="px-4 py-3 text-left">Medicine</th>
                  <th className="px-4 py-3 text-left w-44">Packaging</th>
                  <th className="px-4 py-3 text-left w-28">Quantity</th>
                  <th className="px-4 py-3 text-right w-28">Price</th>
                  <th className="px-4 py-3 text-center w-16">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {rows.map((row, i) => (
                  <tr key={row.id} className="group">
                    <td className="px-4 py-3 text-slate-400 text-xs">{i + 1}</td>

                    {/* Medicine autocomplete */}
                    <td className="px-4 py-3">
                      <div className="relative">
                        <div className="flex items-center">
                          <Search size={14} className="absolute left-2.5 text-slate-300 z-10 pointer-events-none" />
                          <input
                            className="input-field pl-8 pr-8 w-full"
                            placeholder="Type medicine name…"
                            value={row.medicineName}
                            onChange={(e) => handleMedicineInput(row.id, e.target.value)}
                            onFocus={() =>
                              row.suggestions.length > 0 &&
                              setRows((r) => r.map((x) => x.id === row.id ? { ...x, showSuggestions: true } : x))
                            }
                            onBlur={() =>
                              setTimeout(() =>
                                setRows((r) => r.map((x) => x.id === row.id ? { ...x, showSuggestions: false } : x))
                              , 150)
                            }
                          />
                          {row.loadingSuggestions && (
                            <div className="absolute right-2.5 w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                          )}
                          {row.medicine && !row.loadingSuggestions && (
                            <span className="absolute right-2.5 text-emerald-500">
                              <CheckCircle size={14} />
                            </span>
                          )}
                        </div>

                        {/* Suggestions dropdown */}
                        {row.showSuggestions && row.suggestions.length > 0 && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl z-[9999] max-h-52 overflow-y-auto">
                            {row.suggestions.map((m) => (
                              <button
                                key={m.id}
                                onMouseDown={() => selectMedicine(row.id, m)}
                                className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-blue-50 text-left transition-colors"
                              >
                                <div>
                                  <p className="font-medium text-slate-800 text-sm">
        {m.name} {m.default_packaging ? `– ${m.default_packaging}` : ""}
      </p>
                                  {m.name_hindi && <p className="text-xs text-slate-400">{m.name_hindi}</p>}
                                </div>
                                <div className="text-right">
                                  <p className="text-sm text-slate-600">₹{m.price_per_unit}</p>
                                  <p className={`text-xs ${m.stock_quantity > 0 ? "text-emerald-500" : "text-red-500"}`}>
                                    Stock: {m.stock_quantity}
                                  </p>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </td>

                    {/* Packaging */}
                    <td className="px-4 py-3">
  {row.medicine ? (
    <div className="input-field bg-slate-50 text-slate-600 cursor-default">
      {row.packaging || "—"}
    </div>
  ) : (
    <div className="input-field bg-slate-50 text-slate-300 cursor-not-allowed">
      —
    </div>
  )}
</td>

                    {/* Quantity */}
                    <td className="px-4 py-3">
                      {row.medicine ? (
                        <div>
                          <input
                            type="number"
                            min={1}
                            max={row.medicine.stock_quantity}
                            value={row.quantity}
                            onChange={(e) => handleQtyChange(row.id, e.target.value)}
                            className="input-field text-center"
                          />
                          <p className="text-xs text-slate-400 mt-0.5 text-center">max {row.medicine.stock_quantity}</p>
                        </div>
                      ) : (
                        <div className="input-field bg-slate-50 text-slate-300 cursor-not-allowed">—</div>
                      )}
                    </td>

                    {/* Price */}
                    <td className="px-4 py-3 text-right">
                      {row.medicine ? (
                        <span className="font-semibold text-slate-800">
                          ₹{(row.medicine.price_per_unit * row.quantity).toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>

                    {/* Remove */}
                    <td className="px-4 py-3 text-center">
                      <button onClick={() => removeRow(row.id)} className="btn-danger p-1.5">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Sticky Footer */}
      <div className="sticky bottom-0 bg-white border-t border-slate-200 px-6 py-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs text-slate-400 uppercase tracking-wide">Estimated Total</p>
            <p className="text-2xl font-bold text-blue-700">₹{estimateTotal.toFixed(2)}</p>
            <p className="text-xs text-slate-400">
              {validRows.length} medicine{validRows.length !== 1 ? "s" : ""} · {validRows.reduce((s, r) => s + r.quantity, 0)} units
            </p>
          </div>
          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 px-4 py-2 rounded-lg">
              <AlertTriangle size={14} /> {error}
            </div>
          )}
          <div className="flex items-center gap-3">
            <button onClick={handleSaveDraft} disabled={validRows.length === 0} className="btn-secondary flex items-center gap-2">
              <Save size={16} /> {draft ? "Draft Saved ✓" : "Save Draft"}
            </button>
            <button
              onClick={handlePlaceOrder}
              disabled={placing || validRows.length === 0}
              className="btn-primary flex items-center gap-2 px-6 py-2.5"
            >
              <ShoppingBag size={16} />
              {placing ? "Placing…" : "Place Order"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
