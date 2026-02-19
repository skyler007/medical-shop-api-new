import { Phone, Mail, MapPin, Clock, MessageCircle, HelpCircle, Pill } from "lucide-react";

const faqs = [
  { q: "How do I place a manual order?", a: "Go to 'New Order' in the sidebar. Add medicines using the predictive search, select packaging type, enter quantity, fill in customer details, and click 'Place Order'." },
  { q: "What is Chat Order?", a: "Chat Order lets you search medicines conversationally. Type a medicine name or symptom, browse results, and add them to your cart. Then go to Cart to checkout." },
  { q: "Can I save an order as draft?", a: "Yes! In the Manual Order page, click 'Save Draft'. Your draft will be saved locally and you can complete it later." },
  { q: "How do I download an invoice?", a: "Open any order from the Dashboard, then click 'Invoice PDF' button in the top right to download the PDF invoice." },
  { q: "What if a medicine shows out of stock?", a: "If stock is 0, the medicine cannot be ordered. Contact the store manager to replenish stock or choose an alternative." },
  { q: "How are medicine prices calculated?", a: "Prices are based on price_per_unit set for each medicine. Totals are quantity × unit price." },
];

function ContactCard({ icon: Icon, title, value, sub, color }) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon size={18} className="text-white" />
      </div>
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wide">{title}</p>
        <p className="font-semibold text-slate-800 mt-0.5">{value}</p>
        {sub && <p className="text-sm text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export default function Help() {
  return (
    <div className="p-6 space-y-8 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Help & Support</h1>
        <p className="text-slate-500 text-sm mt-0.5">Get help with using Sanjivani Medical Store</p>
      </div>

      {/* Contact Info */}
      <div>
        <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <MessageCircle size={16} /> Contact Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ContactCard icon={Phone}    color="bg-emerald-500" title="Phone"   value="+91-9876543210"        sub="Mon–Sat, 9am – 9pm" />
          <ContactCard icon={Mail}     color="bg-blue-500"    title="Email"   value="info@sanjivanimed.com" sub="Reply within 24 hours" />
          <ContactCard icon={MapPin}   color="bg-violet-500"  title="Address" value="Sanjivani Medical Store" sub="123 Main Street, City, State – 123456" />
          <ContactCard icon={Clock}    color="bg-amber-500"   title="Hours"   value="Mon – Sat: 9am – 9pm"  sub="Sunday: 10am – 6pm" />
        </div>
      </div>

      {/* Quick Guide */}
      <div>
        <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Pill size={16} /> Quick Guide
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: "Manual Order",   steps: ["Click 'New Order'", "Search medicine name", "Select packaging & qty", "Fill customer details", "Click 'Place Order'"] },
            { title: "Chat Order",     steps: ["Click 'Chat Order'", "Type medicine name", "Browse results", "Add to cart", "Go to Cart & checkout"] },
            { title: "View Orders",    steps: ["Go to Dashboard", "See all orders listed", "Click any order row", "View order details", "Download invoice PDF"] },
          ].map((guide) => (
            <div key={guide.title} className="card space-y-3">
              <h3 className="font-medium text-slate-800">{guide.title}</h3>
              <ol className="space-y-1.5">
                {guide.steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div>
        <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <HelpCircle size={16} /> Frequently Asked Questions
        </h2>
        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <details key={i} className="card group">
              <summary className="flex items-center justify-between cursor-pointer font-medium text-slate-800 text-sm list-none">
                {faq.q}
                <span className="text-slate-400 group-open:rotate-180 transition-transform">▾</span>
              </summary>
              <p className="mt-3 text-sm text-slate-500 leading-relaxed">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>

      {/* Footer note */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700">
        <strong>GST Registration:</strong> 22AAAAA0000A1Z5 &nbsp;·&nbsp; <strong>GSTIN:</strong> Sanjivani Medical Store
      </div>
    </div>
  );
}
