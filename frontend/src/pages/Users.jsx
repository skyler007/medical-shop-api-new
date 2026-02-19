import { useState, useEffect } from "react";
import { UserCheck, UserX, Search } from "lucide-react";
import { api } from "../api/client";

const roleBadge = {
  customer:    "bg-blue-100 text-blue-700",
  shopkeeper:  "bg-emerald-100 text-emerald-700",
  admin:       "bg-purple-100 text-purple-700",
};

export default function Users() {
  const [users, setUsers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);

  const load = () => {
    setLoading(true);
    api.getUsers()
      .then((r) => { setUsers(r.data); setFiltered(r.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (!search.trim()) { setFiltered(users); return; }
    const q = search.toLowerCase();
    setFiltered(users.filter((u) =>
      u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    ));
  }, [search, users]);

  const toggleStatus = async (u) => {
    setToggling(u.id);
    try {
      await api.updateUserStatus(u.id, !u.is_active);
      load();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update status.");
    } finally {
      setToggling(null);
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
        <h1 className="text-2xl font-bold text-slate-800">Users</h1>
        <span className="text-sm text-slate-400">{users.length} total</span>
      </div>

      <div className="relative w-72">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input className="input-field pl-8" placeholder="Search users…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                <th className="px-5 py-3 text-left">Name</th>
                <th className="px-5 py-3 text-left">Email</th>
                <th className="px-5 py-3 text-left">Phone</th>
                <th className="px-5 py-3 text-left">Role</th>
                <th className="px-5 py-3 text-left">Joined</th>
                <th className="px-5 py-3 text-left">Status</th>
                <th className="px-5 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-5 py-10 text-center text-slate-400">No users found.</td></tr>
              )}
              {filtered.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3 font-medium text-slate-800">{u.name}</td>
                  <td className="px-5 py-3 text-slate-500">{u.email}</td>
                  <td className="px-5 py-3 text-slate-500">{u.phone || "—"}</td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${roleBadge[u.role] || "bg-slate-100 text-slate-600"}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-500">
                    {new Date(u.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "2-digit" })}
                  </td>
                  <td className="px-5 py-3">
                    {u.is_active
                      ? <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded font-medium">Active</span>
                      : <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded font-medium">Inactive</span>
                    }
                  </td>
                  <td className="px-5 py-3 text-center">
                    <button
                      onClick={() => toggleStatus(u)}
                      disabled={toggling === u.id}
                      className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors ${
                        u.is_active
                          ? "text-red-600 hover:bg-red-50"
                          : "text-green-600 hover:bg-green-50"
                      }`}
                    >
                      {u.is_active ? <UserX size={14} /> : <UserCheck size={14} />}
                      {toggling === u.id ? "…" : u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
