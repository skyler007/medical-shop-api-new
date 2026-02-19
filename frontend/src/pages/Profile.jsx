import { useState } from "react";
import { User, Phone, Mail, Lock, Save, CheckCircle, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

function Alert({ type, msg }) {
  if (!msg) return null;
  return (
    <div className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm ${type === "success" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
      {type === "success" ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
      {msg}
    </div>
  );
}

export default function Profile() {
  const { user, setUser } = useAuth();
  const [profile, setProfile] = useState({ name: user?.name || "", phone: user?.phone || "" });
  const [pw, setPw] = useState({ current: "", new: "", confirm: "" });
  const [profileStatus, setProfileStatus] = useState({ type: "", msg: "" });
  const [pwStatus, setPwStatus] = useState({ type: "", msg: "" });
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPw, setSavingPw] = useState(false);

  const handleProfileSave = async () => {
    setSavingProfile(true);
    setProfileStatus({ type: "", msg: "" });
    try {
      const res = await api.updateProfile({ name: profile.name, phone: profile.phone || null });
      setUser(res.data);
      localStorage.setItem("user", JSON.stringify(res.data));
      setProfileStatus({ type: "success", msg: "Profile updated successfully!" });
    } catch (err) {
      setProfileStatus({ type: "error", msg: err.response?.data?.detail || "Failed to update profile." });
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePwSave = async () => {
    if (pw.new !== pw.confirm) { setPwStatus({ type: "error", msg: "New passwords do not match." }); return; }
    if (pw.new.length < 6) { setPwStatus({ type: "error", msg: "Password must be at least 6 characters." }); return; }
    setSavingPw(true);
    setPwStatus({ type: "", msg: "" });
    try {
      await api.changePassword({ current_password: pw.current, new_password: pw.new });
      setPwStatus({ type: "success", msg: "Password changed successfully!" });
      setPw({ current: "", new: "", confirm: "" });
    } catch (err) {
      setPwStatus({ type: "error", msg: err.response?.data?.detail || "Failed to change password." });
    } finally {
      setSavingPw(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Profile Settings</h1>
        <p className="text-slate-500 text-sm mt-0.5">Manage your account information</p>
      </div>

      {/* Avatar */}
      <div className="card flex items-center gap-5">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl font-bold text-blue-700">
          {user?.name?.[0]?.toUpperCase()}
        </div>
        <div>
          <p className="font-semibold text-slate-800 text-lg">{user?.name}</p>
          <p className="text-slate-500 text-sm">{user?.email}</p>
          <p className="text-xs text-slate-400 mt-0.5">Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString("en-IN", { month: "long", year: "numeric" }) : "—"}</p>
        </div>
      </div>

      {/* Profile Form */}
      <div className="card space-y-4">
        <h2 className="font-semibold text-slate-800 flex items-center gap-2"><User size={16} /> Personal Information</h2>
        <Alert {...profileStatus} />
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Full Name</label>
            <input className="input-field" value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Phone</label>
            <input className="input-field" placeholder="+91 ..." value={profile.phone} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
            <input className="input-field bg-slate-50 cursor-not-allowed" value={user?.email || ""} readOnly />
            <p className="text-xs text-slate-400 mt-1">Email cannot be changed</p>
          </div>
        </div>
        <button onClick={handleProfileSave} disabled={savingProfile} className="btn-primary flex items-center gap-2">
          <Save size={15} /> {savingProfile ? "Saving…" : "Save Changes"}
        </button>
      </div>

      {/* Password Form */}
      <div className="card space-y-4">
        <h2 className="font-semibold text-slate-800 flex items-center gap-2"><Lock size={16} /> Change Password</h2>
        <Alert {...pwStatus} />
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Current Password</label>
          <input type="password" className="input-field" placeholder="••••••••" value={pw.current} onChange={(e) => setPw({ ...pw, current: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">New Password</label>
            <input type="password" className="input-field" placeholder="Min 6 chars" value={pw.new} onChange={(e) => setPw({ ...pw, new: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Confirm New</label>
            <input type="password" className="input-field" placeholder="Repeat new password" value={pw.confirm} onChange={(e) => setPw({ ...pw, confirm: e.target.value })} />
          </div>
        </div>
        <button onClick={handlePwSave} disabled={savingPw || !pw.current || !pw.new} className="btn-primary flex items-center gap-2">
          <Lock size={15} /> {savingPw ? "Saving…" : "Change Password"}
        </button>
      </div>
    </div>
  );
}
