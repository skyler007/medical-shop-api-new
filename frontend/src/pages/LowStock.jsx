import { useState, useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { api } from "../api/client";

export default function LowStock() {
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMedicines(0, 500)
      .then((r) => setMedicines(r.data.filter((m) => m.stock_quantity < 5)))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center gap-3">
        <AlertTriangle size={22} className="text-amber-500" />
        <h1 className="text-2xl font-bold text-slate-800">Low Stock</h1>
        <span className="bg-amber-100 text-amber-700 text-xs font-medium px-2.5 py-0.5 rounded-full">
          {medicines.length} medicines
        </span>
      </div>

      {medicines.length === 0 ? (
        <div className="card text-center py-12 text-slate-400">
          All medicines have sufficient stock.
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <th className="px-5 py-3 text-left w-16">S.No.</th>
                <th className="px-5 py-3 text-left">Medicine Name</th>
                <th className="px-5 py-3 text-left">Category</th>
                <th className="px-5 py-3 text-left">Rack</th>
                <th className="px-5 py-3 text-right">Quantity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {medicines.map((m, i) => (
                <tr key={m.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3 text-slate-400 font-medium">{i + 1}</td>
                  <td className="px-5 py-3">
                    <p className="font-medium text-slate-800">{m.name}</p>
                    {m.generic_name && <p className="text-xs text-slate-400">{m.generic_name}</p>}
                  </td>
                  <td className="px-5 py-3 text-slate-500">{m.category || "—"}</td>
                  <td className="px-5 py-3 text-slate-500">{m.rack_location || "—"}</td>
                  <td className="px-5 py-3 text-right">
                    <span className={`font-bold text-base ${m.stock_quantity === 0 ? "text-red-600" : "text-amber-600"}`}>
                      {m.stock_quantity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
