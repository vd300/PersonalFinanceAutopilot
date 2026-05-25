"use client";

import { useEffect, useMemo, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import { currentMonth, formatDate, formatMoney } from "@/lib/format";
import type { BreakdownItem, Dashboard } from "@/types/api";

function Bars({ items }: { items: BreakdownItem[] }) {
  const max = useMemo(() => Math.max(1, ...items.map((item) => item.amount)), [items]);
  if (!items.length) return <p className="muted">No spend data yet.</p>;
  return (
    <div>
      {items.map((item) => (
        <div className="bar-row" key={item.name}>
          <span>{item.name.replaceAll("_", " ")}</span>
          <span className="bar-track">
            <span className="bar-fill" style={{ width: `${Math.max(5, (item.amount / max) * 100)}%` }} />
          </span>
          <strong>{formatMoney(item.amount)}</strong>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const [month, setMonth] = useState(currentMonth());
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setData(await apiFetch<Dashboard>(`/dashboard?month=${month}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load dashboard");
    }
  }

  useEffect(() => {
    load();
  }, [month]);

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Dashboard</h1>
          <p className="muted">Monthly money picture across all imported sources.</p>
        </div>
        <div className="toolbar">
          <input className="input" type="month" value={month} onChange={(event) => setMonth(event.target.value)} style={{ width: 170 }} />
          <button className="btn" onClick={load} type="button">
            <RefreshCcw size={18} /> Refresh
          </button>
        </div>
      </div>
      {error ? <p className="badge danger">{error}</p> : null}
      {data ? (
        <div className="grid">
          <section className="grid cards">
            <div className="card">
              <div className="metric-label">Safe to spend</div>
              <div className="metric-value safe">{formatMoney(data.safe_to_spend.amount)}</div>
              <p className="muted">{data.safe_to_spend.available_basis}</p>
            </div>
            <div className="card">
              <div className="metric-label">Income</div>
              <div className="metric-value">{formatMoney(data.summary.income)}</div>
            </div>
            <div className="card">
              <div className="metric-label">Expenses</div>
              <div className="metric-value">{formatMoney(data.summary.expenses)}</div>
            </div>
            <div className="card">
              <div className="metric-label">Projected savings</div>
              <div className="metric-value">{formatMoney(data.cashflow_projection.projected_savings)}</div>
            </div>
          </section>

          <section className="grid two">
            <div className="panel">
              <h2>Spending by category</h2>
              <Bars items={data.category_breakdown} />
            </div>
            <div className="panel">
              <h2>Spending by source</h2>
              <Bars items={data.source_breakdown} />
            </div>
          </section>

          <section className="grid two">
            <div className="panel">
              <h2>Largest expenses</h2>
              <div className="table-wrap">
                <table>
                  <tbody>
                    {data.largest_expenses.map((expense) => (
                      <tr key={expense.id}>
                        <td>{formatDate(expense.date)}</td>
                        <td>{expense.merchant}</td>
                        <td>{expense.category}</td>
                        <td><strong>{formatMoney(expense.amount)}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="panel">
              <h2>Upcoming bills</h2>
              {data.upcoming_bills.length ? data.upcoming_bills.map((bill) => (
                <p key={bill.id}><strong>{bill.name}</strong> {formatMoney(bill.expected_amount)} due {formatDate(bill.next_due_date)}</p>
              )) : <p className="muted">No upcoming bills in the next 30 days.</p>}
            </div>
          </section>

          <section className="panel">
            <h2>Safe-to-spend explanation</h2>
            <p className="muted">{data.safe_to_spend.explanation}</p>
            <div className="toolbar">
              {Object.entries(data.safe_to_spend.deductions).map(([key, value]) => (
                <span className="badge" key={key}>{key.replaceAll("_", " ")}: {formatMoney(value)}</span>
              ))}
            </div>
          </section>
        </div>
      ) : (
        <p className="muted">Loading dashboard...</p>
      )}
    </AppShell>
  );
}

