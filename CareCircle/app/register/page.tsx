"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, saveAuth, type AuthSession, type ConfirmationPending } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (fullName.trim().length < 2) {
      setError("Enter your full name.");
      return;
    }
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
      const response = await api<AuthSession | ConfirmationPending>("/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          email,
          phone: phone || null,
          password,
        }),
      });
      if ("confirmation_required" in response) {
        setNotice(response.message);
        return;
      }
      saveAuth(response.access_token, response.user);
      router.replace("/family");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Registration failed.");
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
        <h1 style={{ marginTop: 0 }}>Create a family account</h1>
        {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
        {notice ? <div className="cc-alert success" role="status">{notice}</div> : null}
        <div className="cc-field">
          <label htmlFor="fullName">Full name</label>
          <input id="fullName" value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" />
        </div>
        <div className="cc-field">
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" />
        </div>
        <div className="cc-field">
          <label htmlFor="phone">Phone, optional</label>
          <input id="phone" value={phone} onChange={(event) => setPhone(event.target.value)} autoComplete="tel" />
        </div>
        <div className="cc-field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" />
        </div>
        <button className="cc-button" type="submit" style={{ width: "100%" }} disabled={loading}>
          {loading ? "Creating account..." : "Create account"}
        </button>
        <p className="cc-muted" style={{ marginBottom: 0, textAlign: "center" }}>
          Already registered? <Link href="/login"><strong>Sign in</strong></Link>
        </p>
      </form>
    </main>
  );
}
