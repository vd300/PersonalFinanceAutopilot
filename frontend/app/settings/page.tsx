"use client";

import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import type { FinancialMode, FinancialProfile } from "@/types/api";

type ProfileForm = {
  financial_mode: FinancialMode;
  available_balance: string;
  monthly_income_amount: string;
  monthly_income_day: string;
  expected_income_amount: string;
  expected_income_date: string;
  monthly_essential_expense_estimate: string;
  monthly_non_essential_expense_estimate: string;
  minimum_emergency_buffer: string;
  savings_goal_amount: string;
  credit_card_due_amount: string;
  credit_card_due_date: string;
};

const modeLabels: Record<FinancialMode, string> = {
  salaried: "Salaried",
  freelancer: "Freelancer",
  unemployed: "Unemployed",
  student_dependent: "Student / dependent",
  custom: "Custom"
};

const modeHelp: Record<FinancialMode, string> = {
  salaried: "Safe-to-spend uses balance, expected income, bills, card dues, savings goal, and buffer.",
  freelancer: "Cashflow safety uses confirmed expected income and essential expenses until the next income date.",
  unemployed: "Runway uses balance minus emergency buffer, divided by essential monthly expenses.",
  student_dependent: "Allowance remaining uses balance plus allowance, then reserves bills, essentials, and buffer.",
  custom: "Custom mode uses the conservative safe-to-spend formula with essential expenses reserved."
};

function toForm(profile: FinancialProfile): ProfileForm {
  return {
    financial_mode: profile.financial_mode,
    available_balance: String(profile.available_balance ?? "0"),
    monthly_income_amount: nullableString(profile.monthly_income_amount),
    monthly_income_day: nullableString(profile.monthly_income_day),
    expected_income_amount: nullableString(profile.expected_income_amount),
    expected_income_date: profile.expected_income_date ?? "",
    monthly_essential_expense_estimate: String(profile.monthly_essential_expense_estimate ?? "0"),
    monthly_non_essential_expense_estimate: nullableString(
      profile.monthly_non_essential_expense_estimate
    ),
    minimum_emergency_buffer: String(profile.minimum_emergency_buffer ?? "0"),
    savings_goal_amount: String(profile.savings_goal_amount ?? "0"),
    credit_card_due_amount: nullableString(profile.credit_card_due_amount),
    credit_card_due_date: profile.credit_card_due_date ?? ""
  };
}

function nullableString(value: string | number | null) {
  return value === null || value === undefined ? "" : String(value);
}

function requiredNumber(value: string) {
  return value.trim() === "" ? 0 : Number(value);
}

function optionalNumber(value: string) {
  return value.trim() === "" ? null : Number(value);
}

function optionalDate(value: string) {
  return value.trim() === "" ? null : value;
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<ProfileForm | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<FinancialProfile>("/financial-profile")
      .then((payload) => setProfile(toForm(payload)))
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load profile"));
  }, []);

  function updateField<K extends keyof ProfileForm>(field: K, value: ProfileForm[K]) {
    if (!profile) return;
    setSaved(false);
    setProfile({ ...profile, [field]: value });
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!profile) return;
    setError("");
    const payload = {
      financial_mode: profile.financial_mode,
      available_balance: requiredNumber(profile.available_balance),
      monthly_income_amount: optionalNumber(profile.monthly_income_amount),
      monthly_income_day: optionalNumber(profile.monthly_income_day),
      expected_income_amount: optionalNumber(profile.expected_income_amount),
      expected_income_date: optionalDate(profile.expected_income_date),
      monthly_essential_expense_estimate: requiredNumber(
        profile.monthly_essential_expense_estimate
      ),
      monthly_non_essential_expense_estimate: optionalNumber(
        profile.monthly_non_essential_expense_estimate
      ),
      minimum_emergency_buffer: requiredNumber(profile.minimum_emergency_buffer),
      savings_goal_amount: requiredNumber(profile.savings_goal_amount),
      credit_card_due_amount: optionalNumber(profile.credit_card_due_amount),
      credit_card_due_date: optionalDate(profile.credit_card_due_date)
    };

    try {
      const updated = await apiFetch<FinancialProfile>("/financial-profile", {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      setProfile(toForm(updated));
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save profile");
    }
  }

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Settings</h1>
          <p className="muted">Configure the financial profile used by the dashboard.</p>
        </div>
      </div>
      {error ? <p className="badge danger">{error}</p> : null}
      <section className="panel">
        {profile ? (
          <form className="form wide" onSubmit={submit}>
            <label>
              <span className="metric-label">Financial mode</span>
              <select
                className="select"
                value={profile.financial_mode}
                onChange={(event) => updateField("financial_mode", event.target.value as FinancialMode)}
              >
                {Object.entries(modeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <p className="field-note">{modeHelp[profile.financial_mode]}</p>

            <div className="form-grid">
              <label>
                <span className="metric-label">Available balance</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.available_balance}
                  onChange={(event) => updateField("available_balance", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Monthly income amount</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.monthly_income_amount}
                  onChange={(event) => updateField("monthly_income_amount", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Monthly income day</span>
                <input
                  className="input"
                  max="31"
                  min="1"
                  type="number"
                  value={profile.monthly_income_day}
                  onChange={(event) => updateField("monthly_income_day", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Expected income amount</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.expected_income_amount}
                  onChange={(event) => updateField("expected_income_amount", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Expected income date</span>
                <input
                  className="input"
                  type="date"
                  value={profile.expected_income_date}
                  onChange={(event) => updateField("expected_income_date", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Monthly essential expenses</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.monthly_essential_expense_estimate}
                  onChange={(event) =>
                    updateField("monthly_essential_expense_estimate", event.target.value)
                  }
                />
              </label>
              <label>
                <span className="metric-label">Monthly non-essential expenses</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.monthly_non_essential_expense_estimate}
                  onChange={(event) =>
                    updateField("monthly_non_essential_expense_estimate", event.target.value)
                  }
                />
              </label>
              <label>
                <span className="metric-label">Minimum emergency buffer</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.minimum_emergency_buffer}
                  onChange={(event) => updateField("minimum_emergency_buffer", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Savings goal</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.savings_goal_amount}
                  onChange={(event) => updateField("savings_goal_amount", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Credit card due amount</span>
                <input
                  className="input"
                  min="0"
                  type="number"
                  value={profile.credit_card_due_amount}
                  onChange={(event) => updateField("credit_card_due_amount", event.target.value)}
                />
              </label>
              <label>
                <span className="metric-label">Credit card due date</span>
                <input
                  className="input"
                  type="date"
                  value={profile.credit_card_due_date}
                  onChange={(event) => updateField("credit_card_due_date", event.target.value)}
                />
              </label>
            </div>

            <div className="toolbar">
              <button className="btn primary" type="submit">
                <Save size={18} /> Save profile
              </button>
              {saved ? <span className="badge">Saved</span> : null}
            </div>
          </form>
        ) : (
          <p className="muted">Loading financial profile...</p>
        )}
      </section>
    </AppShell>
  );
}
