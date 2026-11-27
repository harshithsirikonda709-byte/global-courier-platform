"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type ParentProfile, type Visit } from "@/lib/api";

export default function FamilyVisitsPage() {
  const [parents, setParents] = useState<ParentProfile[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [parentId, setParentId] = useState("");
  const [scheduledStart, setScheduledStart] = useState("");
  const [duration, setDuration] = useState("60");
  const [requirements, setRequirements] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const [parentResults, visitResults] = await Promise.all([
      api<ParentProfile[]>("/v1/carecircle/parents"),
      api<Visit[]>("/v1/carecircle/visits"),
    ]);
    setParents(parentResults);
    setVisits(visitResults);
    setParentId((current) => current || parentResults[0]?.id || "");
  }, []);

  useEffect(() => {
    let active = true;
    Promise.all([
      api<ParentProfile[]>("/v1/carecircle/parents"),
      api<Visit[]>("/v1/carecircle/visits"),
    ]).then(([parentResults, visitResults]) => {
      if (!active) return;
      setParents(parentResults);
      setVisits(visitResults);
      setParentId(parentResults[0]?.id || "");
    }).catch((requestError: unknown) => {
      if (active) setError(requestError instanceof Error ? requestError.message : "Unable to load visits.");
    });
    return () => { active = false; };
  }, []);

  async function bookVisit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Visit>("/v1/carecircle/visits", {
        method: "POST",
        body: JSON.stringify({
          parent_id: parentId,
          scheduled_start: new Date(scheduledStart).toISOString(),
          duration_minutes: Number(duration),
          requirements: requirements.trim() || null,
        }),
      });
      setNotice("Visit request submitted. A verified, approved companion must be assigned.");
      setRequirements("");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to book visit.");
    } finally {
      setBusy(false);
    }
  }

  async function cancelVisit(visitId: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Visit>(`/v1/carecircle/visits/${visitId}/cancel`, {
        method: "POST",
        body: JSON.stringify({ reason: "Cancelled by family" }),
      });
      setNotice("Visit cancelled.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to cancel visit.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>Visits</h1>
          <p className="cc-muted">Request non-medical companionship and view visit history.</p>
        </div>
        <Link className="cc-button secondary" href="/family/parents">Parent profiles</Link>
      </div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      {notice ? <div className="cc-alert success" role="status">{notice}</div> : null}

      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Request a visit</h2>
        <p className="cc-muted">Visits are companionship only, not medical or nursing care. Current personal consent from the parent is required.</p>
        {parents.length ? (
          <form onSubmit={bookVisit}>
            <div className="cc-field">
              <label htmlFor="parentId">Parent</label>
              <select id="parentId" value={parentId} onChange={(event) => setParentId(event.target.value)} required>
                {parents.map((parent) => <option key={parent.id} value={parent.id}>{parent.full_name}</option>)}
              </select>
            </div>
            <div className="cc-grid cc-grid-two">
              <div className="cc-field">
                <label htmlFor="scheduledStart">Preferred date and time</label>
                <input id="scheduledStart" type="datetime-local" value={scheduledStart} onChange={(event) => setScheduledStart(event.target.value)} required />
              </div>
              <div className="cc-field">
                <label htmlFor="duration">Duration</label>
                <select id="duration" value={duration} onChange={(event) => setDuration(event.target.value)}>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                  <option value="90">1.5 hours</option>
                  <option value="120">2 hours</option>
                  <option value="180">3 hours</option>
                  <option value="240">4 hours</option>
                </select>
              </div>
            </div>
            <div className="cc-field">
              <label htmlFor="requirements">Companionship preferences or requirements</label>
              <textarea id="requirements" value={requirements} onChange={(event) => setRequirements(event.target.value)} maxLength={2000} placeholder="Activities, communication preferences, or accessibility needs. Do not enter medical instructions." />
            </div>
            <button className="cc-button" type="submit" disabled={busy || !scheduledStart}>{busy ? "Submitting..." : "Request visit"}</button>
          </form>
        ) : <p className="cc-muted">Add a parent profile before requesting a visit.</p>}
      </section>

      <section className="cc-card cc-card-pad">
        <h2>Visit history</h2>
        {visits.length ? visits.map((visit) => (
          <article key={visit.id} style={{ borderTop: "1px solid #e5e9f2", padding: "14px 0" }}>
            <strong>{parents.find((parent) => parent.id === visit.parent_id)?.full_name || "Parent visit"}</strong>
            <p className="cc-muted">{new Date(visit.scheduled_start).toLocaleString()} · {visit.duration_minutes} minutes</p>
            <p><span className="cc-status">{visit.status.replaceAll("_", " ")}</span>{visit.companion_id ? " · Companion assigned" : ""}</p>
            {visit.requirements ? <p>{visit.requirements}</p> : null}
            {["requested", "assigned", "accepted"].includes(visit.status) ? (
              <button type="button" className="cc-button danger" disabled={busy} onClick={() => cancelVisit(visit.id)}>Cancel visit</button>
            ) : null}
          </article>
        )) : <p className="cc-muted">No visits have been requested.</p>}
      </section>
    </>
  );
}
