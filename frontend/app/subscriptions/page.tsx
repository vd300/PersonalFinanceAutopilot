"use client";

import { useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import { formatDate, formatMoney } from "@/lib/format";

type Subscription = {
  id: string;
  merchant_name: string;
  amount: number;
  frequency: string;
  last_payment_date: string;
  next_expected_payment_date: string;
  status: string;
  confidence_score: number;
};

export default function SubscriptionsPage() {
  const [items, setItems] = useState<Subscription[]>([]);
  async function load() {
    setItems(await apiFetch<Subscription[]>("/subscriptions"));
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Subscriptions</h1>
          <p className="muted">Recurring payments detected from similar merchants and amounts.</p>
        </div>
        <button className="btn" onClick={async () => { await apiFetch("/subscriptions/detect", { method: "POST" }); await load(); }} type="button">
          <RefreshCcw size={18} /> Detect
        </button>
      </div>
      <section className="grid cards">
        {items.map((item) => (
          <article className="card" key={item.id}>
            <div className="metric-label">{item.status} · {item.confidence_score}% confidence</div>
            <div className="metric-value">{item.merchant_name}</div>
            <p>{formatMoney(item.amount)} {item.frequency}</p>
            <p className="muted">Next expected {formatDate(item.next_expected_payment_date)}</p>
          </article>
        ))}
      </section>
    </AppShell>
  );
}

