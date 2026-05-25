"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";

type Alert = { id: string; alert_type: string; title: string; message: string; severity: string; status: string; created_at: string };

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  async function load() {
    setAlerts(await apiFetch<Alert[]>("/alerts"));
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Alerts</h1>
          <p className="muted">Overspending, unusual transactions, subscription, and bill notices.</p>
        </div>
      </div>
      <section className="grid">
        {alerts.map((alert) => (
          <article className="panel" key={alert.id}>
            <div className="page-title">
              <div>
                <span className={`badge ${alert.severity === "high" ? "danger" : alert.severity === "medium" ? "warning" : ""}`}>{alert.alert_type.replaceAll("_", " ")}</span>
                <h2>{alert.title}</h2>
                <p className="muted">{alert.message}</p>
              </div>
              {alert.status === "active" ? (
                <button className="btn" type="button" onClick={async () => { await apiFetch(`/alerts/${alert.id}/dismiss`, { method: "PATCH" }); await load(); }}>
                  <Check size={18} /> Dismiss
                </button>
              ) : <span className="badge">dismissed</span>}
            </div>
          </article>
        ))}
      </section>
    </AppShell>
  );
}

