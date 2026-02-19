import { createContext, useContext, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);

  const addItem = (medicine, packaging, quantity) => {
    setItems((prev) => {
      const exists = prev.find(
        (i) => i.medicine_id === medicine.id && i.packaging_type === packaging
      );
      if (exists) {
        return prev.map((i) =>
          i.medicine_id === medicine.id && i.packaging_type === packaging
            ? { ...i, quantity: i.quantity + quantity, total_price: (i.quantity + quantity) * i.price_per_unit }
            : i
        );
      }
      return [
        ...prev,
        {
          medicine_id: medicine.id,
          medicine_name: medicine.name,
          packaging_type: packaging,
          quantity,
          price_per_unit: medicine.price_per_unit,
          total_price: quantity * medicine.price_per_unit,
          stock_quantity: medicine.stock_quantity,
        },
      ];
    });
  };

  const removeItem = (medicine_id, packaging_type) => {
    setItems((prev) =>
      prev.filter((i) => !(i.medicine_id === medicine_id && i.packaging_type === packaging_type))
    );
  };

  const updateQuantity = (medicine_id, packaging_type, quantity) => {
    setItems((prev) =>
      prev.map((i) =>
        i.medicine_id === medicine_id && i.packaging_type === packaging_type
          ? { ...i, quantity, total_price: quantity * i.price_per_unit }
          : i
      )
    );
  };

  const clearCart = () => setItems([]);

  const total = items.reduce((s, i) => s + i.total_price, 0);

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, updateQuantity, clearCart, total }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
