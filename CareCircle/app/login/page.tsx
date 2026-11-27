"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, saveAuth, type AuthUser } from "@/lib/api";

type AuthResponse = { access_token: string; user: AuthUser };

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (!email.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }
    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      const response = await api<AuthResponse>("/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveAuth(response.access_token, response.user);
      router.replace(
        response.user.is_admin ? "/admin" :
          response.user.account_type === "companion" ? "/companion" :
            response.user.account_type === "parent" ? "/parent" : "/family",
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Sign-in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="cc-auth-layout">
      <form className="cc-card cc-card-pad cc-auth-card" onSubmit={submit} noValidate>
        <div className="cc-brand" style={{ color: "#172033", marginBottom: 12 }}>
          CARE<span style={{ color: "#3159a8" }}>CIRCLE</span>
        </div>
        <h1 style={{ marginTop: 0 }}>Family sign in</h1>
        {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
        <div className="cc-field">
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" />
        </div>
        <div className="cc-field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
        </div>
        <button className="cc-button" type="submit" style={{ width: "100%" }} disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
        <p className="cc-muted" style={{ marginBottom: 0, textAlign: "center" }}>
          New family? <Link href="/register"><strong>Create an account</strong></Link>
        </p>
      </form>
    </main>
  );
}
