"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogIn, Play } from "lucide-react";
import { demoLogin, login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("demo1234");
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <main className="auth-page">
      <section className="panel auth-card">
        <div className="page-title">
          <div>
            <h1>Login</h1>
            <p className="muted">Use the demo account or your own workspace.</p>
          </div>
        </div>
        <form className="form" onSubmit={submit}>
          <input className="input" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
          <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" />
          {error ? <p className="badge danger">{error}</p> : null}
          <button className="btn primary" type="submit">
            <LogIn size={18} /> Login
          </button>
          <button
            className="btn"
            type="button"
            onClick={async () => {
              await demoLogin();
              router.push("/dashboard");
            }}
          >
            <Play size={18} /> Use demo data
          </button>
        </form>
        <p className="muted">
          New here? <Link href="/signup">Create an account</Link>
        </p>
      </section>
    </main>
  );
}

