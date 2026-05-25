"use client";

import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import { currentMonth, formatDate, formatMoney } from "@/lib/format";
import type { Transaction } from "@/types/api";

export default function TransactionsPage() {
  const [month, setMonth] = useState(currentMonth());
  const [search, setSearch] = useState("");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [error, setError] = useState("");

  async function load() {
    const params = new URLSearchParams({ month });
    if (search) params.set("search", search);
    try {
      setTransactions(await apiFetch<Transaction[]>(`/transactions?${params.toString()}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load transactions");
    }
  }

  useEffect(() => {
    load();
  }, [month]);

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Transactions</h1>
          <p className="muted">Review normalized imports, unusual flags, duplicates, and categories.</p>
        </div>
        <div className="toolbar">
          <input className="input" type="month" value={month} onChange={(event) => setMonth(event.target.value)} style={{ width: 170 }} />
          <input className="input" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search merchant" style={{ width: 220 }} />
          <button className="btn" onClick={load} type="button"><Search size={18} /> Search</button>
        </div>
      </div>
      {error ? <p className="badge danger">{error}</p> : null}
      <section className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant</th>
                <th>Category</th>
                <th>Source</th>
                <th>Method</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{formatDate(tx.transaction_date)}</td>
                  <td>{tx.display_name || tx.merchant_name || tx.raw_description}</td>
                  <td>{tx.category || "Other"}</td>
                  <td>{tx.source_type.replaceAll("_", " ")}</td>
                  <td>{tx.payment_method.replaceAll("_", " ")}</td>
                  <td><span className="badge">{tx.transaction_type}</span></td>
                  <td><strong>{formatMoney(tx.amount)}</strong></td>
                  <td className="toolbar">
                    {tx.is_unusual ? <span className="badge warning">unusual</span> : null}
                    {tx.is_duplicate ? <span className="badge">duplicate</span> : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}

