"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type ParentProfile } from "@/lib/api";

export default function ParentsPage() {
  const [parents, setParents] = useState<ParentProfile[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<ParentProfile[]>("/v1/carecircle/parents")
      .then(setParents)
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load parent profiles."));
  }, []);

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>My Parents</h1>
          <p className="cc-muted">Profiles you are authorized to manage.</p>
        </div>
        <Link className="cc-button" href="/family/parents/new">Add parent</Link>
      </div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      <div className="cc-grid cc-grid-two">
        {parents.map((parent) => {
          const activeConsent = parent.consents.find((consent) => consent.status === "active");
          return (
            <Link key={parent.id} href={`/family/parents/${parent.id}`} className="cc-card cc-card-pad cc-parent-card">
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <h2 style={{ marginTop: 0 }}>{parent.full_name}</h2>
                <span className={`cc-status ${activeConsent ? "" : "withdrawn"}`}>{activeConsent ? "Consent active" : "No active consent"}</span>
              </div>
              <p className="cc-muted">{parent.address_line1}, {parent.city}</p>
              <p><strong>Language:</strong> {parent.preferred_language}</p>
              <p><strong>Emergency contacts:</strong> {parent.emergency_contacts.length}</p>
            </Link>
          );
        })}
      </div>
    </>
  );
}
