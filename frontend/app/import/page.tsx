"use client";

import { useEffect, useState } from "react";
import { Check, Upload } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { apiFetch } from "@/lib/api";
import { formatMoney } from "@/lib/format";

type Source = { value: string; label: string };
type Preview = {
  upload_id: string;
  status: string;
  total_rows: number;
  failed_rows: number;
  error_message: string | null;
  warnings: string[];
  transactions: Array<{ transaction_date: string; amount: number; merchant_name: string | null; transaction_type: string; source_type: string; raw_description: string }>;
};

export default function ImportPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [sourceType, setSourceType] = useState("google_pay");
  const [file, setFile] = useState<File | null>(null);
  const [pdfPassword, setPdfPassword] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const isPdf = file?.name.toLowerCase().endsWith(".pdf") ?? false;

  useEffect(() => {
    apiFetch<Source[]>("/import/sources").then(setSources).catch((err) => setError(err.message));
  }, []);

  async function uploadFile(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;
    setError("");
    setResult("");
    const form = new FormData();
    form.append("source_type", sourceType);
    if (isPdf && pdfPassword) {
      form.append("pdf_password", pdfPassword);
    }
    form.append("file", file);
    try {
      setPreview(await apiFetch<Preview>("/import/upload", { method: "POST", body: form }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  }

  async function confirm() {
    if (!preview) return;
    setError("");
    try {
      const response = await apiFetch<{ imported_rows: number; duplicate_rows: number; failed_rows: number }>(`/import/uploads/${preview.upload_id}/confirm`, {
        method: "POST"
      });
      setResult(`Imported ${response.imported_rows} rows, found ${response.duplicate_rows} duplicates, and skipped ${response.failed_rows} failed rows.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Confirm import failed");
    }
  }

  return (
    <AppShell>
      <div className="page-title">
        <div>
          <h1>Import transactions</h1>
          <p className="muted">Upload PDF, CSV, or Excel exports from payment apps, cards, wallets, or bank statements.</p>
        </div>
      </div>
      <section className="panel">
        <form className="form" onSubmit={uploadFile}>
          <label>
            <span className="metric-label">Source</span>
            <select className="select" value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
              {sources.map((source) => <option key={source.value} value={source.value}>{source.label}</option>)}
            </select>
          </label>
          <label>
            <span className="metric-label">File</span>
            <input className="input" type="file" accept=".pdf,.csv,.xlsx,.xls,.xlsm" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          </label>
          {isPdf ? (
            <label>
              <span className="metric-label">PDF password, if protected</span>
              <input
                className="input"
                type="password"
                value={pdfPassword}
                onChange={(event) => setPdfPassword(event.target.value)}
                autoComplete="off"
              />
            </label>
          ) : null}
          <button className="btn primary" type="submit">
            <Upload size={18} /> Parse preview
          </button>
        </form>
        {error ? <p className="badge danger">{error}</p> : null}
        {result ? <p className="badge">{result}</p> : null}
      </section>

      {preview ? (
        <section className="panel" style={{ marginTop: 16 }}>
          <div className="page-title">
            <div>
              <h2>Preview</h2>
              <p className="muted">{preview.total_rows} rows parsed, {preview.failed_rows} failed.</p>
            </div>
            <button
              className="btn primary"
              type="button"
              onClick={confirm}
              disabled={preview.status === "failed" || preview.transactions.length === 0}
            >
              <Check size={18} /> Confirm import
            </button>
          </div>
          {preview.error_message ? <p className="badge danger">{preview.error_message}</p> : null}
          {preview.warnings.length ? (
            <div style={{ marginTop: 12 }}>
              {preview.warnings.map((warning) => <p className="badge" key={warning}>{warning}</p>)}
            </div>
          ) : null}
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Merchant</th>
                  <th>Description</th>
                  <th>Type</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {preview.transactions.map((tx, index) => (
                  <tr key={`${tx.transaction_date}-${index}`}>
                    <td>{tx.transaction_date}</td>
                    <td>{tx.merchant_name}</td>
                    <td>{tx.raw_description}</td>
                    <td><span className="badge">{tx.transaction_type}</span></td>
                    <td>{formatMoney(Number(tx.amount))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </AppShell>
  );
}
