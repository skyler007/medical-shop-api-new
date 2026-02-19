import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, ShoppingCart, MessageSquare, ClipboardList,
  User, HelpCircle, LogOut, Pill, Users, Package, AlertTriangle
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const roleLinks = {
  customer: [
    { to: "/",             icon: LayoutDashboard, label: "Dashboard"  },
    { to: "/order/manual", icon: ClipboardList,   label: "New Order"  },
    { to: "/order/chat",   icon: MessageSquare,   label: "Chat Order" },
    { to: "/cart",         icon: ShoppingCart,    label: "Cart"       },
    { to: "/profile",      icon: User,            label: "Profile"    },
    { to: "/help",         icon: HelpCircle,      label: "Help"       },
  ],
  shopkeeper: [
    { to: "/",             icon: LayoutDashboard, label: "Dashboard"  },
    { to: "/orders",       icon: Package,         label: "Orders"     },
    { to: "/medicines",    icon: Pill,            label: "Medicines"  },
    { to: "/low-stock",    icon: AlertTriangle,   label: "Low Stock"  },
    { to: "/profile",      icon: User,            label: "Profile"    },
    { to: "/help",         icon: HelpCircle,      label: "Help"       },
  ],
  admin: [
    { to: "/",             icon: LayoutDashboard, label: "Dashboard"  },
    { to: "/orders",       icon: Package,         label: "Orders"     },
    { to: "/medicines",    icon: Pill,            label: "Medicines"  },
    { to: "/low-stock",    icon: AlertTriangle,   label: "Low Stock"  },
    { to: "/admin/users",  icon: Users,           label: "Users"      },
    { to: "/profile",      icon: User,            label: "Profile"    },
    { to: "/help",         icon: HelpCircle,      label: "Help"       },
  ],
};

const roleBadge = { customer: "bg-blue-100 text-blue-700", shopkeeper: "bg-emerald-100 text-emerald-700", admin: "bg-purple-100 text-purple-700" };

export default function Sidebar() {
  const { user, logout } = useAuth();
  const { items } = useCart();
  const navigate = useNavigate();

  const role = user?.role || "customer";
  const links = roleLinks[role] || roleLinks.customer;

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <aside className="w-64 min-h-screen bg-white border-r border-slate-100 flex flex-col shadow-sm">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
            <Pill size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800 leading-tight">Sanjivani</p>
            <p className="text-xs text-slate-400">Medical Store</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
            {label === "Cart" && items.length > 0 && (
              <span className="ml-auto bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {items.length}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="px-3 py-4 border-t border-slate-100">
        <div className="flex items-center gap-3 px-3 py-2 mb-1">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-blue-700 text-sm font-semibold">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{user?.name}</p>
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${roleBadge[role]}`}>
              {role}
            </span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}
