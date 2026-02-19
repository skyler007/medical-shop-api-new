import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import OrderDetail from "./pages/OrderDetail";
import ChatOrder from "./pages/ChatOrder";
import Cart from "./pages/Cart";
import ManualOrder from "./pages/ManualOrder";
import Profile from "./pages/Profile";
import Help from "./pages/Help";
import Orders from "./pages/Orders";
import Medicines from "./pages/Medicines";
import Users from "./pages/Users";
import LowStock from "./pages/LowStock";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <CartProvider>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/orders/:id" element={<OrderDetail />} />
                  {/* Customer routes */}
                  <Route path="/order/chat"   element={<ProtectedRoute roles={["customer"]}><ChatOrder /></ProtectedRoute>} />
                  <Route path="/order/manual" element={<ProtectedRoute roles={["customer"]}><ManualOrder /></ProtectedRoute>} />
                  <Route path="/cart"         element={<ProtectedRoute roles={["customer"]}><Cart /></ProtectedRoute>} />
                  {/* Shopkeeper + Admin routes */}
                  <Route path="/orders"       element={<ProtectedRoute roles={["shopkeeper","admin"]}><Orders /></ProtectedRoute>} />
                  <Route path="/medicines"    element={<ProtectedRoute roles={["shopkeeper","admin"]}><Medicines /></ProtectedRoute>} />
                  <Route path="/low-stock"    element={<ProtectedRoute roles={["shopkeeper","admin"]}><LowStock /></ProtectedRoute>} />
                  {/* Admin-only routes */}
                  <Route path="/admin/users"  element={<ProtectedRoute roles={["admin"]}><Users /></ProtectedRoute>} />
                  {/* Shared */}
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/help"    element={<Help />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </CartProvider>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
