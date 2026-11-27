"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type Consent, type ParentProfile } from "@/lib/api";

export default function ParentPortal() {
  const [parent, setParent] = useState<ParentProfile | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [scope, setScope] = useState("Companionship visits");
  const [consentText, setConsentText] = useState("");
  const [withdrawReason, setWithdrawReason] = useState("");

  const refresh = useCallback(async () => {
    setParent(await api<ParentProfile>("/v1/carecircle/parents/me"));
  }, []);

  useEffect(() => {
    let active = true;
    api<ParentProfile>("/v1/carecircle/parents/me").then((parentProfile) => {
      if (active) setParent(parentProfile);
    }).catch((requestError: unknown) => {
      if (active) setError(requestError instanceof Error ? requestError.message : "Unable to load parent profile.");
    });
    return () => { active = false; };
  }, []);

  async function savePreferences(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!parent) return;
    const form = new FormData(event.currentTarget);
    const payload = {
      full_name: String(form.get("full_name")),
      date_of_birth: String(form.get("date_of_birth")) || null,
      gender: parent.gender,
      phone: String(form.get("phone")) || null,
      alternate_phone: parent.alternate_phone,
      address_line1: parent.address_line1,
      address_line2: parent.address_line2,
      city: parent.city,
      state: parent.state,
      postal_code: parent.postal_code,
      country: parent.country,
      address_instructions: parent.address_instructions,
      preferred_language: String(form.get("preferred_language")),
      interests: String(form.get("interests")) || null,
      accessibility_preferences: String(form.get("accessibility_preferences")) || null,
      emergency_contacts: parent.emergency_contacts,
    };
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<ParentProfile>(`/v1/carecircle/parents/${parent.id}`, { method: "PUT", body: JSON.stringify(payload) });
      setNotice("Your preferences have been saved.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save preferences.");
    } finally {
      setBusy(false);
    }
  }

  async function grantConsent(event: React.FormEvent) {
    event.preventDefault();
    if (!parent) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Consent>(`/v1/carecircle/parents/${parent.id}/consents`, {
        method: "POST",
        body: JSON.stringify({ scope, consent_text: consentText }),
      });
      setConsentText("");
      setNotice("Your personal consent has been recorded.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to record consent.");
    } finally {
      setBusy(false);
    }
  }

  async function withdraw(consentId: string) {
    if (!parent) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Consent>(`/v1/carecircle/parents/${parent.id}/consents/${consentId}/withdraw`, {
        method: "POST",
        body: JSON.stringify({ reason: withdrawReason }),
      });
      setWithdrawReason("");
      setNotice("Your consent was withdrawn. New visits cannot be assigned or started.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to withdraw consent.");
    } finally {
      setBusy(false);
    }
  }

  if (!parent) {
    return <div className="cc-card cc-card-pad"><h1>Parent portal</h1><p className={error ? "" : "cc-muted"}>{error || "Loading your profile..."}</p></div>;
  }

  const activeConsent = parent.consents.find((consent) => consent.status === "active" && consent.consent_source === "parent");

  return (
    <>
      <div className="cc-page-header"><div><h1>Your preferences and consent</h1><p className="cc-muted">You control your profile preferences and personal consent.</p></div></div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      {notice ? <div className="cc-alert success" role="status">{notice}</div> : null}
      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Preferences</h2>
        <form onSubmit={savePreferences}>
          <div className="cc-grid cc-grid-two">
            <div className="cc-field"><label htmlFor="full_name">Name</label><input id="full_name" name="full_name" defaultValue={parent.full_name} required /></div>
            <div className="cc-field"><label htmlFor="phone">Phone</label><input id="phone" name="phone" defaultValue={parent.phone || ""} /></div>
            <div className="cc-field"><label htmlFor="date_of_birth">Date of birth</label><input id="date_of_birth" name="date_of_birth" type="date" defaultValue={parent.date_of_birth || ""} /></div>
            <div className="cc-field"><label htmlFor="preferred_language">Preferred language</label><input id="preferred_language" name="preferred_language" defaultValue={parent.preferred_language} required /></div>
          </div>
          <div className="cc-field"><label htmlFor="interests">Interests and preferred activities</label><textarea id="interests" name="interests" defaultValue={parent.interests || ""} /></div>
          <div className="cc-field"><label htmlFor="accessibility_preferences">Accessibility and communication preferences</label><textarea id="accessibility_preferences" name="accessibility_preferences" defaultValue={parent.accessibility_preferences || ""} /></div>
          <button type="submit" className="cc-button" disabled={busy}>{busy ? "Saving..." : "Save preferences"}</button>
        </form>
      </section>
      <section className="cc-card cc-card-pad">
        <h2>Personal consent</h2>
        <p className="cc-muted">This is your decision. Family reports do not count as your personal consent. CareCircle offers companionship, not medical or nursing services.</p>
        {activeConsent ? (
          <>
            <span className="cc-status">Your consent is active</span>
            <p><strong>Scope:</strong> {activeConsent.scope}</p>
            <p>{activeConsent.consent_text}</p>
            <div className="cc-field"><label htmlFor="withdrawReason">Reason for withdrawal</label><input id="withdrawReason" value={withdrawReason} onChange={(event) => setWithdrawReason(event.target.value)} minLength={3} /></div>
            <button type="button" className="cc-button danger" disabled={busy || withdrawReason.trim().length < 3} onClick={() => withdraw(activeConsent.id)}>Withdraw consent</button>
          </>
        ) : (
          <form onSubmit={grantConsent}>
            <div className="cc-field"><label htmlFor="scope">Consent scope</label><input id="scope" value={scope} onChange={(event) => setScope(event.target.value)} required minLength={3} /></div>
            <div className="cc-field"><label htmlFor="consentText">Your consent statement</label><textarea id="consentText" value={consentText} onChange={(event) => setConsentText(event.target.value)} required minLength={10} /></div>
            <button type="submit" className="cc-button" disabled={busy}>{busy ? "Saving..." : "Give personal consent"}</button>
          </form>
        )}
        {parent.consents.some((consent) => consent.status === "family_reported") ? <p className="cc-muted">A family member has recorded a report. It does not activate or replace your personal consent.</p> : null}
      </section>
    </>
  );
}
