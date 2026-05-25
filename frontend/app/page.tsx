import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";

export default function HomePage() {
  return (
    <main className="hero">
      <div className="hero-content">
        <h1>Personal Finance Autopilot</h1>
        <p>
          Import Google Pay, PhonePe, Amazon Pay, OneCard, credit card, and bank exports into one private workspace
          that explains spending, bills, subscriptions, and your estimated safe-to-spend amount.
        </p>
        <div className="toolbar" style={{ marginTop: 26 }}>
          <Link className="btn primary" href="/login">
            Open app <ArrowRight size={18} />
          </Link>
          <Link className="btn" href="/signup">
            <ShieldCheck size={18} /> Create account
          </Link>
        </div>
      </div>
    </main>
  );
}

