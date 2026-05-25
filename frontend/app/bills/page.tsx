"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import { formatDate, formatMoney } from "@/lib/format";

type Bill = { id: string; name: string; expected_amount: number; due_day: number; next_due_date: string; frequency: string; is_auto_detected: boolean; status: string };

export default function BillsPage() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [nextDueDate, setNextDueDate] = useState("");

  async function load() {
    setBills(await apiFetch<Bill[]>("/bills"));
  }

  useEffect(() => {
    load();
  }, []);

  async function addBill(event: React.FormEvent) {
    event.preventDefault();
    const day = Number(nextDueDate.slice(-2)) || 1;
    await apiFetch("/bills", {
      method: "POST",
      body: JSON.stringify({ name, expected_amount: Number(amount), due_day: day, next_due_date: nextDueDate, frequency: "monthly" })
    });
    setName("");
    setAmount("");
    setNextDueDate("");
    await load();
  }

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Bills</h1>
          <p className="muted">Upcoming commitments that reduce safe-to-spend.</p>
        </div>
      </div>
      <section className="grid two">
        <div className="panel">
          <h2>Add bill</h2>
          <form className="form" onSubmit={addBill}>
            <input className="input" value={name} onChange={(event) => setName(event.target.value)} placeholder="Name" />
            <input className="input" type="number" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="Expected amount" />
            <input className="input" type="date" value={nextDueDate} onChange={(event) => setNextDueDate(event.target.value)} />
            <button className="btn primary" type="submit"><Plus size={18} /> Add bill</button>
          </form>
        </div>
        <div className="panel">
          <h2>Upcoming</h2>
          {bills.map((bill) => (
            <p key={bill.id}>
              <strong>{bill.name}</strong> {formatMoney(bill.expected_amount)} due {formatDate(bill.next_due_date)} <span className="badge">{bill.status}</span>
            </p>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

