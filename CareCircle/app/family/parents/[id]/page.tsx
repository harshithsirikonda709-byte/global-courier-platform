"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Suspense } from "react";
import { useCallback, useEffect, useState } from "react";
import { api, type Consent, type ParentProfile } from "@/lib/api";

function ParentDetailContent() {
  const params = useParams<{ id: string }>();
  const [parent, setParent] = useState<ParentProfile | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [consentText, setConsentText] = useState("The parent told me they agree to scheduled, non-medical companionship visits.");
  const [scope, setScope] = useState("Scheduled companionship visits");
  const [withdrawReason, setWithdrawReason] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setParent(await api<ParentProfile>(`/v1/carecircle/parents/${params.id}`));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to load parent.");
    }
  }, [params.id]);

  useEffect(() => {
    load();
  }, [load]);

  async function recordConsent(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (consentText.trim().length < 10) {
      setError("Enter a complete consent statement.");
      return;
    }
    setBusy(true);
    try {
      await api<Consent>(`/v1/carecircle/parents/${params.id}/consents`, {
        method: "POST",
        body: JSON.stringify({
          scope,
          consent_text: consentText,
        }),
      });
      setSuccess("Your report was recorded. It is not treated as the parent's personal consent.");
      setWithdrawReason("");
      await load();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to record consent.");
    } finally {
      setBusy(false);
    }
  }

  async function withdrawConsent(consentId: string) {
    setError("");
    setSuccess("");
    if (withdrawReason.trim().length < 3) {
      setError("Enter a reason for withdrawing consent.");
      return;
    }
    setBusy(true);
    try {
      await api<Consent>(`/v1/carecircle/parents/${params.id}/consents/${consentId}/withdraw`, {
        method: "POST",
        body: JSON.stringify({ reason: withdrawReason }),
      });
      setSuccess("Consent withdrawn. Future visits should stop.");
      await load();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to withdraw consent.");
    } finally {
      setBusy(false);
    }
  }

  if (!parent) {
    return (
      <>
        {error ? <div className="cc-alert error" role="alert">{error}</div> : <p className="cc-muted">Loading parent profile...</p>}
      </>
    );
  }

  const activeConsent = parent.consents.find((consent) => consent.status === "active");

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>{parent.full_name}</h1>
          <p className="cc-muted">Parent profile and consent</p>
        </div>
        <Link className="cc-button" href={`/family/parents/${parent.id}/edit`}>Update profile</Link>
      </div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      {success ? <div className="cc-alert success" role="status">{success}</div> : null}

      <div className="cc-grid cc-grid-two">
        <section className="cc-card cc-card-pad">
          <h2>Personal Details</h2>
          <p><strong>Phone:</strong> {parent.phone || "Not provided"}</p>
          <p><strong>Date of birth:</strong> {parent.date_of_birth || "Not provided"}</p>
          <p><strong>Gender:</strong> {parent.gender || "Not volunteered"}</p>
          <p><strong>Preferred language:</strong> {parent.preferred_language}</p>
          <p><strong>Interests:</strong> {parent.interests || "Not provided"}</p>
          <p><strong>Accessibility:</strong> {parent.accessibility_preferences || "Not provided"}</p>
        </section>

        <section className="cc-card cc-card-pad">
          <h2>Address</h2>
          <p>{parent.address_line1}</p>
          {parent.address_line2 ? <p>{parent.address_line2}</p> : null}
          <p>{parent.city}, {parent.state} {parent.postal_code}</p>
          <p>{parent.country}</p>
          {parent.address_instructions ? <p><strong>Entry instructions:</strong> {parent.address_instructions}</p> : null}
        </section>
      </div>

      <section className="cc-card cc-card-pad" style={{ marginTop: 20 }}>
        <h2>Emergency Contacts</h2>
        {parent.emergency_contacts.length ? parent.emergency_contacts.map((contact) => (
          <div key={contact.id ?? contact.phone} style={{ borderBottom: "1px solid #e5e9f2", padding: "8px 0" }}>
            <strong>{contact.full_name}</strong>{contact.relationship ? ` — ${contact.relationship}` : ""}
            <p className="cc-muted" style={{ margin: "4px 0" }}>{contact.phone}{contact.alternate_phone ? ` · Alternate: ${contact.alternate_phone}` : ""}</p>
          </div>
        )) : <p className="cc-muted">No emergency contact has been stored.</p>}
      </section>

      <section className="cc-card cc-card-pad" style={{ marginTop: 20 }}>
        <h2>Consent</h2>
        {activeConsent ? (
          <>
            <span className="cc-status">Active</span>
            <p><strong>Scope:</strong> {activeConsent.scope}</p>
            <p>{activeConsent.consent_text}</p>
            <div className="cc-field">
              <label htmlFor="withdrawReason">Withdrawal reason</label>
              <input id="withdrawReason" value={withdrawReason} onChange={(event) => setWithdrawReason(event.target.value)} />
            </div>
            <button type="button" className="cc-button danger" disabled={busy} onClick={() => withdrawConsent(activeConsent.id)}>
              {busy ? "Processing..." : "Withdraw consent"}
            </button>
          </>
        ) : (
          <>
            <p className="cc-muted">
              Family members can record what the parent said, but only the parent&apos;s own authenticated account can grant personal consent.
            </p>
            <form onSubmit={recordConsent} noValidate>
            <div className="cc-field">
              <label htmlFor="scope">Consent scope</label>
              <input id="scope" value={scope} onChange={(event) => setScope(event.target.value)} />
            </div>
            <div className="cc-field">
              <label htmlFor="consentText">What did the parent say?</label>
              <textarea id="consentText" value={consentText} onChange={(event) => setConsentText(event.target.value)} />
            </div>
            <button type="submit" className="cc-button" disabled={busy}>
              {busy ? "Saving..." : "Record family report"}
            </button>
            </form>
          </>
        )}

        {parent.consents.length ? (
          <div style={{ marginTop: 20 }}>
            <h3>Consent History</h3>
            {parent.consents.map((consent) => (
              <div key={consent.id} style={{ borderTop: "1px solid #e5e9f2", padding: "12px 0" }}>
                <span className={`cc-status ${consent.status === "withdrawn" ? "withdrawn" : ""}`}>{consent.status}</span>
                <span className="cc-muted"> · {consent.consent_source === "parent" ? "Parent-authenticated" : "Family report; not personal consent"}</span>
                <p style={{ marginBottom: 4 }}>{consent.scope}</p>
                {consent.withdrawal_reason ? <p className="cc-muted">Withdrawal: {consent.withdrawal_reason}</p> : null}
              </div>
            ))}
          </div>
        ) : null}
      </section>
    </>
  );
}

export default function ParentDetailPage() {
  return (
    <Suspense fallback={<p className="cc-muted">Loading parent profile...</p>}>
      <ParentDetailContent />
    </Suspense>
  );
}
