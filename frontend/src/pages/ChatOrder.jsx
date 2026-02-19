import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, ShoppingCart, RotateCcw } from "lucide-react";
import { api } from "../api/client";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";

const PACKAGING = ["strip", "bottle", "box", "loose", "tube", "vial"];

const HELP_MSG = `I can help you search and add medicines to your cart.

Try saying:
• "I need Paracetamol"
• "Search for Crocin"
• "Add 2 strips of Amoxicillin"
• "What medicines do you have for fever?"`;

function Message({ msg }) {
  const isBot = msg.role === "bot";
  return (
    <div className={`flex gap-3 ${isBot ? "" : "flex-row-reverse"}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isBot ? "bg-blue-100" : "bg-emerald-100"}`}>
        {isBot ? <Bot size={16} className="text-blue-600" /> : <User size={16} className="text-emerald-600" />}
      </div>
      <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${isBot ? "bg-white border border-slate-100 text-slate-700" : "bg-blue-600 text-white"}`}>
        {msg.content}
        {msg.medicines && (
          <div className="mt-3 space-y-2">
            {msg.medicines.map((m, i) => (
              <MedicineCard key={i} medicine={m} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MedicineCard({ medicine }) {
  const { addItem } = useCart();
  const [qty, setQty] = useState(1);
  const [pack, setPack] = useState(medicine.default_packaging || "strip");
  const [added, setAdded] = useState(false);

  const handleAdd = () => {
    addItem(medicine, pack, qty);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-700">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold text-slate-800">{medicine.name}</p>
          {medicine.name_hindi && <p className="text-xs text-slate-400">{medicine.name_hindi}</p>}
          <p className="text-xs text-slate-500 mt-0.5">₹{medicine.price_per_unit}/unit · Stock: {medicine.stock_quantity}</p>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full ${medicine.stock_quantity > 0 ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
          {medicine.stock_quantity > 0 ? "In Stock" : "Out of Stock"}
        </span>
      </div>
      {medicine.stock_quantity > 0 && (
        <div className="flex items-center gap-2 mt-2">
          <select value={pack} onChange={(e) => setPack(e.target.value)} className="text-xs border border-slate-200 rounded px-2 py-1 bg-white">
            {PACKAGING.map((p) => <option key={p}>{p}</option>)}
          </select>
          <input type="number" min={1} max={medicine.stock_quantity} value={qty} onChange={(e) => setQty(Math.min(Number(e.target.value), medicine.stock_quantity))}
            className="w-16 text-xs border border-slate-200 rounded px-2 py-1 text-center" />
          <button onClick={handleAdd} className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${added ? "bg-emerald-500 text-white" : "bg-blue-600 text-white hover:bg-blue-700"}`}>
            {added ? "Added ✓" : "Add to Cart"}
          </button>
        </div>
      )}
    </div>
  );
}

export default function ChatOrder() {
  const [messages, setMessages] = useState([
    { role: "bot", content: `Hello! I'm your medicine assistant. ${HELP_MSG}` }
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef(null);
  const navigate = useNavigate();
  const { items } = useCart();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setThinking(true);

    try {
      // Extract medicine names from the message
      const res = await api.searchMedicines(text, 5);
      const medicines = res.data.medicines;

      let reply;
      if (medicines.length === 0) {
        reply = { role: "bot", content: `Sorry, I couldn't find any medicine matching "${text}". Please try a different name or check the spelling.` };
      } else {
        reply = {
          role: "bot",
          content: `Found ${medicines.length} medicine${medicines.length > 1 ? "s" : ""} for "${text}":`,
          medicines,
        };
      }
      setMessages((m) => [...m, reply]);
    } catch {
      setMessages((m) => [...m, { role: "bot", content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setThinking(false);
    }
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(input); };

  const reset = () => setMessages([{ role: "bot", content: `Hello! ${HELP_MSG}` }]);

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-100 rounded-full flex items-center justify-center">
            <Bot size={18} className="text-blue-600" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-800">Medicine Assistant</h1>
            <p className="text-xs text-emerald-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full inline-block" /> Online
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={reset} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors" title="Reset chat">
            <RotateCcw size={16} />
          </button>
          {items.length > 0 && (
            <button onClick={() => navigate("/cart")} className="btn-primary flex items-center gap-2 text-sm py-2">
              <ShoppingCart size={15} /> Cart ({items.length})
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((msg, i) => <Message key={i} msg={msg} />)}
        {thinking && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <Bot size={16} className="text-blue-600" />
            </div>
            <div className="bg-white border border-slate-100 rounded-2xl px-4 py-3 flex items-center gap-1">
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 bg-white border-t border-slate-100">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            className="input-field flex-1"
            placeholder="Type a medicine name or describe your symptoms…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={thinking}
          />
          <button type="submit" disabled={thinking || !input.trim()} className="btn-primary px-4">
            <Send size={17} />
          </button>
        </form>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Search medicines, check availability, and add to cart
        </p>
      </div>
    </div>
  );
}
