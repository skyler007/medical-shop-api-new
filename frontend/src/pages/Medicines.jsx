import { useState, useEffect } from "react";
import { Plus, Search, Edit2, Trash2, X, AlertTriangle } from "lucide-react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

const EMPTY_FORM = {
  name: "", name_hindi: "", generic_name: "", company: "", category: "",
  price_per_unit: "", mrp: "", stock_quantity: "", reorder_level: "10",
  default_packaging: "strip", batch_number: "", rack_location: "",
};

export default function Medicines() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [medicines, setMedicines] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // null | "add" | "edit"
  const [form, setForm] = useState(EMPTY_FORM);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    api.getMedicines(0, 500)
      .then((r) => { setMedicines(r.data); setFiltered(r.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (!search.trim()) { setFiltered(medicines); return; }
    const q = search.toLowerCase();
    setFiltered(medicines.filter((m) =>
      m.name.toLowerCase().includes(q) ||
      (m.generic_name || "").toLowerCase().includes(q) ||
      (m.category || "").toLowerCase().includes(q)
    ));
  }, [search, medicines]);

  const openAdd = () => { setForm(EMPTY_FORM); setEditId(null); setError(""); setModal("add"); };
  const openEdit = (m) => {
    setForm({
      name: m.name || "", name_hindi: m.name_hindi || "", generic_name: m.generic_name || "",
      company: m.company || "", category: m.category || "",
      price_per_unit: m.price_per_unit ?? "", mrp: m.mrp ?? "",
      stock_quantity: m.stock_quantity ?? "", reorder_level: m.reorder_level ?? "10",
      default_packaging: m.default_packaging || "strip",
      batch_number: m.batch_number || "", rack_location: m.rack_location || "",
    });
    setEditId(m.id);
    setError("");
    setModal("edit");
  };

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = {
      ...form,
      price_per_unit: parseFloat(form.price_per_unit),
      mrp: parseFloat(form.mrp),
      stock_quantity: parseInt(form.stock_quantity),
      reorder_level: parseInt(form.reorder_level),
    };
    try {
      if (modal === "add") {
        await api.createMedicine(payload);
      } else {
        await api.updateMedicine(editId, payload);
      }
      setModal(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      await api.deleteMedicine(id);
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Delete failed.");
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Medicines</h1>
        <button onClick={openAdd} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Add Medicine
        </button>
      </div>

      {/* Search */}
      <div className="relative w-72">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input className="input-field pl-8" placeholder="Search medicines…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">Category</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">MRP</th>
                <th className="px-4 py-3 text-right">Stock</th>
                <th className="px-4 py-3 text-left">Rack</th>
                <th className="px-4 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-10 text-center text-slate-400">No medicines found.</td></tr>
              )}
              {filtered.map((m) => (
                <tr key={m.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-800">{m.name}</p>
                    {m.generic_name && <p className="text-xs text-slate-400">{m.generic_name}</p>}
                  </td>
                  <td className="px-4 py-3 text-slate-500">{m.category || "—"}</td>
                  <td className="px-4 py-3 text-right text-slate-700">₹{m.price_per_unit}</td>
                  <td className="px-4 py-3 text-right text-slate-700">₹{m.mrp}</td>
                  <td className="px-4 py-3 text-right">
                    <span className={m.stock_quantity <= m.reorder_level ? "text-red-600 font-semibold flex items-center justify-end gap-1" : "text-slate-700"}>
                      {m.stock_quantity <= m.reorder_level && <AlertTriangle size={13} />}
                      {m.stock_quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500">{m.rack_location || "—"}</td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button onClick={() => openEdit(m)} className="text-blue-600 hover:text-blue-800">
                        <Edit2 size={15} />
                      </button>
                      {isAdmin && (
                        <button onClick={() => handleDelete(m.id, m.name)} className="text-red-500 hover:text-red-700">
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-slate-100 text-xs text-slate-400">
          {filtered.length} of {medicines.length} medicines
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="font-semibold text-slate-800">{modal === "add" ? "Add Medicine" : "Edit Medicine"}</h2>
              <button onClick={() => setModal(null)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <form onSubmit={handleSave} className="px-6 py-4 space-y-3">
              {error && <p className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="label">Name *</label>
                  <input className="input-field" value={form.name} onChange={set("name")} required />
                </div>
                <div>
                  <label className="label">Hindi Name</label>
                  <input className="input-field" value={form.name_hindi} onChange={set("name_hindi")} />
                </div>
                <div>
                  <label className="label">Generic Name</label>
                  <input className="input-field" value={form.generic_name} onChange={set("generic_name")} />
                </div>
                <div>
                  <label className="label">Company</label>
                  <input className="input-field" value={form.company} onChange={set("company")} />
                </div>
                <div>
                  <label className="label">Category</label>
                  <input className="input-field" value={form.category} onChange={set("category")} />
                </div>
                <div>
                  <label className="label">Price/Unit (₹) *</label>
                  <input type="number" step="0.01" className="input-field" value={form.price_per_unit} onChange={set("price_per_unit")} required />
                </div>
                <div>
                  <label className="label">MRP (₹) *</label>
                  <input type="number" step="0.01" className="input-field" value={form.mrp} onChange={set("mrp")} required />
                </div>
                <div>
                  <label className="label">Stock Qty *</label>
                  <input type="number" className="input-field" value={form.stock_quantity} onChange={set("stock_quantity")} required />
                </div>
                <div>
                  <label className="label">Reorder Level</label>
                  <input type="number" className="input-field" value={form.reorder_level} onChange={set("reorder_level")} />
                </div>
                <div>
                  <label className="label">Batch Number</label>
                  <input className="input-field" value={form.batch_number} onChange={set("batch_number")} />
                </div>
                <div>
                  <label className="label">Rack Location</label>
                  <input className="input-field" value={form.rack_location} onChange={set("rack_location")} />
                </div>
                <div>
                  <label className="label">Packaging</label>
                  <select className="input-field" value={form.default_packaging} onChange={set("default_packaging")}>
                    {["strip", "bottle", "box", "loose", "tube", "vial"].map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setModal(null)} className="btn-secondary flex-1">Cancel</button>
                <button type="submit" disabled={saving} className="btn-primary flex-1">
                  {saving ? "Saving…" : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
