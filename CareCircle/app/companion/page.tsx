"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type Availability, type CompanionProfile, type Visit } from "@/lib/api";

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function blankAvailability(): Availability[] {
  return DAYS.map((_, weekday) => ({ weekday, start_time: "09:00", end_time: "17:00" }));
}

export default function CompanionWorkspace() {
  const [profile, setProfile] = useState<CompanionProfile | null>(null);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [enabledDays, setEnabledDays] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const [profileResult, schedule, visitResults] = await Promise.all([
      api<CompanionProfile>("/v1/carecircle/companions/me"),
      api<Availability[]>("/v1/carecircle/companions/me/availability"),
      api<Visit[]>("/v1/carecircle/companion/visits"),
    ]);
    setProfile(profileResult);
    setAvailability(schedule.length ? schedule : blankAvailability());
    setEnabledDays(schedule.map((slot) => slot.weekday));
    setVisits(visitResults);
  }, []);

  useEffect(() => {
    let active = true;
    Promise.all([
      api<CompanionProfile>("/v1/carecircle/companions/me"),
      api<Availability[]>("/v1/carecircle/companions/me/availability"),
      api<Visit[]>("/v1/carecircle/companion/visits"),
    ]).then(([profileResult, schedule, visitResults]) => {
      if (!active) return;
      setProfile(profileResult);
      setAvailability(schedule.length ? schedule : blankAvailability());
      setEnabledDays(schedule.map((slot) => slot.weekday));
      setVisits(visitResults);
    }).catch((requestError: unknown) => {
      if (active) setError(requestError instanceof Error ? requestError.message : "Unable to load companion workspace.");
    });
    return () => { active = false; };
  }, []);

  async function saveProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profile) return;
    const formData = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const saved = await api<CompanionProfile>("/v1/carecircle/companions/me", {
        method: "PUT",
        body: JSON.stringify({
          display_name: formData.get("display_name"),
          bio: formData.get("bio"),
          languages: String(formData.get("languages")).split(","),
          service_area: formData.get("service_area"),
          timezone_name: formData.get("timezone_name"),
          identity_document_type: formData.get("identity_document_type"),
        }),
      });
      setProfile(saved);
      setNotice("Profile submitted for admin review. Identity verification is not complete until an admin checks your document.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save profile.");
    } finally {
      setBusy(false);
    }
  }

  async function saveAvailability() {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const schedule = availability.filter((slot) => enabledDays.includes(slot.weekday));
      const saved = await api<Availability[]>("/v1/carecircle/companions/me/availability", {
        method: "PUT",
        body: JSON.stringify({ availability: schedule }),
      });
      setEnabledDays(saved.map((slot) => slot.weekday));
      setNotice("Availability saved.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save availability.");
    } finally {
      setBusy(false);
    }
  }

  async function respond(visitId: string, action: "accept" | "reject") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Visit>(`/v1/carecircle/visits/${visitId}/${action}`, {
        method: "POST",
        body: JSON.stringify(action === "reject" ? { reason: "Unable to accept this visit" } : {}),
      });
      setNotice(action === "accept" ? "Visit accepted." : "Visit returned to the assignment queue.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : `Unable to ${action} visit.`);
    } finally {
      setBusy(false);
    }
  }

  async function updateVisit(visitId: string, action: "check-in" | "check-out") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api<Visit>(`/v1/carecircle/visits/${visitId}/${action}`, { method: "POST" });
      setNotice(action === "check-in" ? "Visit checked in." : "Visit completed.");
      await refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to update visit.");
    } finally {
      setBusy(false);
    }
  }

  function updateSlot(weekday: number, field: "start_time" | "end_time", value: string) {
    setAvailability((current) => current.map((slot) => slot.weekday === weekday ? { ...slot, [field]: value } : slot));
  }

  if (!profile) return <p className="cc-muted">{error || "Loading companion workspace..."}</p>;

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>Companion workspace</h1>
          <p className="cc-muted">Complete your profile and availability for non-medical companionship visits.</p>
        </div>
        <span className="cc-status">{profile.approval_status.replaceAll("_", " ")}</span>
      </div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      {notice ? <div className="cc-alert success" role="status">{notice}</div> : null}
      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Companion profile</h2>
        <p className="cc-muted">Identity document details are reviewed by an administrator. Do not upload or enter a document number here.</p>
        <form onSubmit={saveProfile}>
          <div className="cc-field"><label htmlFor="display_name">Display name</label><input id="display_name" name="display_name" defaultValue={profile.display_name} required minLength={2} /></div>
          <div className="cc-field"><label htmlFor="bio">About you</label><textarea id="bio" name="bio" defaultValue={profile.bio} required minLength={20} maxLength={2000} /></div>
          <div className="cc-field"><label htmlFor="languages">Languages (comma-separated)</label><input id="languages" name="languages" defaultValue={profile.languages.join(", ")} required /></div>
          <div className="cc-grid cc-grid-two">
            <div className="cc-field"><label htmlFor="service_area">Service area</label><input id="service_area" name="service_area" defaultValue={profile.service_area} required /></div>
            <div className="cc-field"><label htmlFor="timezone_name">Time zone</label><input id="timezone_name" name="timezone_name" defaultValue={profile.timezone_name || "Asia/Kolkata"} required /></div>
          </div>
          <div className="cc-field"><label htmlFor="identity_document_type">Identity document type for admin review</label><input id="identity_document_type" name="identity_document_type" defaultValue={profile.identity_document_type} placeholder="For example, government photo ID" required /></div>
          <p className="cc-muted">Identity: {profile.identity_status}. Approval: {profile.approval_status}. Visits cannot be assigned until both are approved.</p>
          {profile.admin_notes ? <p className="cc-alert">{profile.admin_notes}</p> : null}
          <button type="submit" className="cc-button" disabled={busy}>{busy ? "Saving..." : "Save profile"}</button>
        </form>
      </section>

      <section className="cc-card cc-card-pad" style={{ marginBottom: 20 }}>
        <h2>Weekly availability</h2>
        <p className="cc-muted">Hours use the time zone in your profile.</p>
        {availability.map((slot) => (
          <div key={slot.weekday} className="cc-grid cc-grid-three" style={{ alignItems: "center" }}>
            <label><input type="checkbox" checked={enabledDays.includes(slot.weekday)} onChange={(event) => setEnabledDays((days) => event.target.checked ? [...days, slot.weekday] : days.filter((day) => day !== slot.weekday))} /> {DAYS[slot.weekday]}</label>
            <div className="cc-field"><label htmlFor={`start-${slot.weekday}`}>From</label><input id={`start-${slot.weekday}`} type="time" value={slot.start_time.slice(0, 5)} onChange={(event) => updateSlot(slot.weekday, "start_time", event.target.value)} /></div>
            <div className="cc-field"><label htmlFor={`end-${slot.weekday}`}>To</label><input id={`end-${slot.weekday}`} type="time" value={slot.end_time.slice(0, 5)} onChange={(event) => updateSlot(slot.weekday, "end_time", event.target.value)} /></div>
          </div>
        ))}
        <button type="button" className="cc-button" disabled={busy} onClick={saveAvailability}>Save availability</button>
      </section>

      <section className="cc-card cc-card-pad">
        <h2>Assigned visits</h2>
        {visits.length ? visits.map((visit) => (
          <article key={visit.id} style={{ borderTop: "1px solid #e5e9f2", padding: "14px 0" }}>
            <strong>{new Date(visit.scheduled_start).toLocaleString()}</strong>
            <p>{visit.duration_minutes} minutes · <span className="cc-status">{visit.status.replaceAll("_", " ")}</span></p>
            {visit.requirements ? <p>{visit.requirements}</p> : null}
            {visit.status === "assigned" ? <div className="cc-actions"><button className="cc-button" disabled={busy} onClick={() => respond(visit.id, "accept")}>Accept</button><button className="cc-button danger" disabled={busy} onClick={() => respond(visit.id, "reject")}>Reject</button></div> : null}
            {visit.status === "accepted" ? <button className="cc-button" disabled={busy} onClick={() => updateVisit(visit.id, "check-in")}>Check in</button> : null}
            {visit.status === "in_progress" ? <button className="cc-button" disabled={busy} onClick={() => updateVisit(visit.id, "check-out")}>Check out and complete</button> : null}
          </article>
        )) : <p className="cc-muted">No visits assigned yet.</p>}
      </section>
    </>
  );
}
