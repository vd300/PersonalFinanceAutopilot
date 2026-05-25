"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserPlus } from "lucide-react";
import { signup } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await signup(name, email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    }
  }

  return (
    <main className="auth-page">
      <section className="panel auth-card">
        <div className="page-title">
          <div>
            <h1>Create account</h1>
            <p className="muted">Your imported finance data stays in your app database.</p>
          </div>
        </div>
        <form className="form" onSubmit={submit}>
          <input className="input" value={name} onChange={(event) => setName(event.target.value)} placeholder="Name" />
          <input className="input" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
          <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" />
          {error ? <p className="badge danger">{error}</p> : null}
          <button className="btn primary" type="submit">
            <UserPlus size={18} /> Sign up
          </button>
        </form>
        <p className="muted">
          Already have an account? <Link href="/login">Login</Link>
        </p>
      </section>
    </main>
  );
}

