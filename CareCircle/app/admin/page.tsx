"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type CompanionProfile, type Visit } from "@/lib/api";

type AdminCompanion = CompanionProfile & { email: string; phone?: string | null };

export default function AdminReviewPage() {
  const [pending, setPending] = useState<AdminCompanion[]>([]);
  const [approved, setApproved] = useState<AdminCompanion[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [selectedCompanions, setSelectedCompanions] = useState<Record<string, string>>({});
  const [parentId, setParentId] = useState("");
  const [parentUserId, setParentUserId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const [pendingResults, approvedResults, visitResults] = await Promise.all([
      api<AdminCompanion[]>("/v1/carecircle/admin/companions?approval_status=pending"),
      api<AdminCompanion[]>("/v1/carecircle/admin/companions?approval_status=approved"),
      api<Visit[]>("/v1/carecircle/admin/visits?status_filter=requested"),
    ]);
    setPending(pendingResults);
    setApproved(approvedResults.filter((companion) => companion.identity_status === "verified"));
    setVisits(visitResults);
  }, []);

  useEffect(() => {
    let active = true;
    Promise.all([
      api<AdminCompanion[]>("/v1/carecircle/admin/companions?approval_status=pending"),
      api<AdminCompanion[]>("/v1/carecircle/admin/companions?approval_status=approved"),
      api<Visit[]>("/v1/carecircle/admin/visits?status_filter=requested"),
    ]).then(([pendingResults, approvedResults, visitResults]) => {
      if (!active) return;
      setPending(pendingResults);
      setApproved(approvedResults.filter((companion) => companion.identity_status === "verified"));
      setVisits(visitResults);
    }).catch((requestError: unknown) => {
      if (active) setError(requestError instanceof Error ? requestError.message : "Unable to load admin queue.");
    });
    return () => { active = false; };
  }, []);

  async function review(companion: AdminCompanion, action: "verify_identity" | "approve" | "reject_identity" | "reject") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<AdminCompanion>(`/v1/carecircle/admin/companions/${companion.id}/review`, {
        method: "POST",
        body: JSON.stringify({ action, notes: action === "verify_identity" ? "Identity reviewed by platform administrator" : null }),
      });
      setNotice(`Companion ${action.replaceAll("_", " ")} complete.`);
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to review companion.");
    } finally {
      setBusy(false);
    }
  }

  async function assign(visitId: string) {
    const companionId = selectedCompanions[visitId];
    if (!companionId) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Visit>(`/v1/carecircle/admin/visits/${visitId}/assign`, {
        method: "POST",
        body: JSON.stringify({ companion_id: companionId }),
      });
      setNotice("Approved companion assigned.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to assign companion.");
    } finally {
      setBusy(false);
    }
  }

  async function linkParent(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<void>(`/v1/carecircle/admin/parents/${parentId}/link`, {
        method: "POST",
        body: JSON.stringify({ parent_user_id: parentUserId }),
      });
      setNotice("Parent profile linked to the authenticated platform account.");
      setParentId("");
      setParentUserId("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to link parent.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="cc-page-header"><div><h1>Admin review</h1><p className="cc-muted">Verify companions and assign visits only to approved, available companions.</p></div></div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      {notice ? <div className="cc-alert success" role="status">{notice}</div> : null}
      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Companion approvals</h2>
        {pending.length ? pending.map((companion) => (
          <article key={companion.id} style={{ borderTop: "1px solid #e5e9f2", padding: "14px 0" }}>
            <h3>{companion.display_name}</h3>
            <p>{companion.email}{companion.phone ? ` · ${companion.phone}` : ""} · {companion.service_area}</p>
            <p>{companion.bio}</p>
            <p>Languages: {companion.languages.join(", ")} · Identity document: {companion.identity_document_type}</p>
            <p>Identity: {companion.identity_status} · Approval: {companion.approval_status}</p>
            {companion.admin_notes ? <p className="cc-muted">Review note: {companion.admin_notes}</p> : null}
            <div className="cc-actions">
              {companion.identity_status === "pending" ? <><button className="cc-button" disabled={busy} onClick={() => review(companion, "verify_identity")}>Mark identity verified</button><button className="cc-button danger" disabled={busy} onClick={() => review(companion, "reject_identity")}>Reject identity</button></> : null}
              {companion.identity_status === "verified" && companion.approval_status === "pending" ? <><button className="cc-button" disabled={busy} onClick={() => review(companion, "approve")}>Approve companion</button><button className="cc-button danger" disabled={busy} onClick={() => review(companion, "reject")}>Reject application</button></> : null}
            </div>
          </article>
        )) : <p className="cc-muted">No companions awaiting approval.</p>}
      </section>
      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Requested visits</h2>
        {visits.length ? visits.map((visit) => (
          <article key={visit.id} style={{ borderTop: "1px solid #e5e9f2", padding: "14px 0" }}>
            <p><strong>{new Date(visit.scheduled_start).toLocaleString()}</strong> · {visit.duration_minutes} minutes</p>
            <p>Parent: {visit.parent_id} · Family: {visit.family_id}</p>
            <p>{visit.requirements || "No additional requirements"} · Status: {visit.status}</p>
            {approved.length ? (
              <div className="cc-actions">
                <select aria-label="Approved companion" value={selectedCompanions[visit.id] || ""} onChange={(event) => setSelectedCompanions((current) => ({ ...current, [visit.id]: event.target.value }))}>
                  <option value="">Select an approved companion</option>
                  {approved.map((companion) => <option key={companion.id} value={companion.id}>{companion.display_name} · {companion.service_area}</option>)}
                </select>
                <button className="cc-button" disabled={busy || !selectedCompanions[visit.id]} onClick={() => assign(visit.id)}>Assign</button>
              </div>
            ) : <p className="cc-muted">No verified, approved companion available in the queue.</p>}
          </article>
        )) : <p className="cc-muted">No requested visits.</p>}
      </section>
      <section className="cc-card cc-card-pad">
        <h2>Link a parent account</h2>
        <p className="cc-muted">Only link after verifying the person’s identity through the organization’s approved process.</p>
        <form onSubmit={linkParent}>
          <div className="cc-grid cc-grid-two">
            <div className="cc-field"><label htmlFor="parentId">Parent profile ID</label><input id="parentId" value={parentId} onChange={(event) => setParentId(event.target.value)} required /></div>
            <div className="cc-field"><label htmlFor="parentUserId">Supabase user ID</label><input id="parentUserId" value={parentUserId} onChange={(event) => setParentUserId(event.target.value)} required /></div>
          </div>
          <button className="cc-button" disabled={busy}>Link verified parent</button>
        </form>
      </section>
    </>
  );
}
