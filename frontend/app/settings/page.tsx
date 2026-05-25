"use client";

import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";

type Settings = {
  preferred_currency: string;
  monthly_income_day: number;
  savings_goal_amount: number;
  minimum_buffer_amount: number;
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiFetch<Settings>("/settings").then(setSettings);
  }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!settings) return;
    setSettings(await apiFetch<Settings>("/settings", { method: "PATCH", body: JSON.stringify(settings) }));
    setSaved(true);
  }

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Settings</h1>
          <p className="muted">Configure the inputs used for safe-to-spend and projections.</p>
        </div>
      </div>
      <section className="panel">
        {settings ? (
          <form className="form" onSubmit={submit}>
            <label>
              <span className="metric-label">Currency</span>
              <input className="input" value={settings.preferred_currency} onChange={(event) => setSettings({ ...settings, preferred_currency: event.target.value })} />
            </label>
            <label>
              <span className="metric-label">Monthly income day</span>
              <input className="input" type="number" min="1" max="31" value={settings.monthly_income_day} onChange={(event) => setSettings({ ...settings, monthly_income_day: Number(event.target.value) })} />
            </label>
            <label>
              <span className="metric-label">Savings goal</span>
              <input className="input" type="number" value={settings.savings_goal_amount} onChange={(event) => setSettings({ ...settings, savings_goal_amount: Number(event.target.value) })} />
            </label>
            <label>
              <span className="metric-label">Minimum buffer</span>
              <input className="input" type="number" value={settings.minimum_buffer_amount} onChange={(event) => setSettings({ ...settings, minimum_buffer_amount: Number(event.target.value) })} />
            </label>
            <button className="btn primary" type="submit"><Save size={18} /> Save settings</button>
            {saved ? <span className="badge">Saved</span> : null}
          </form>
        ) : (
          <p className="muted">Loading settings...</p>
        )}
      </section>
    </AppShell>
  );
}

