"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type ParentProfile } from "@/lib/api";

export default function FamilyDashboard() {
  const [parents, setParents] = useState<ParentProfile[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<ParentProfile[]>("/v1/carecircle/parents")
      .then(setParents)
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load parents."));
  }, []);

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>Family Dashboard</h1>
          <p className="cc-muted">Manage parent profiles and consent.</p>
        </div>
        <Link className="cc-button" href="/family/parents/new">Add parent</Link>
      </div>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}
      <div className="cc-grid cc-grid-three">
        {parents.map((parent) => {
          const activeConsent = parent.consents.find((consent) => consent.status === "active");
          return (
            <Link key={parent.id} href={`/family/parents/${parent.id}`} className="cc-card cc-card-pad cc-parent-card">
              <h2 style={{ marginTop: 0 }}>{parent.full_name}</h2>
              <p className="cc-muted">{parent.city}, {parent.state}</p>
              <p><strong>Language:</strong> {parent.preferred_language}</p>
              <span className={`cc-status ${activeConsent ? "" : "withdrawn"}`}>
                {activeConsent ? "Consent active" : "Consent required"}
              </span>
            </Link>
          );
        })}
        {parents.length === 0 && !error ? (
          <div className="cc-card cc-empty" style={{ gridColumn: "1 / -1" }}>
            <h2>No parent profiles yet</h2>
            <p className="cc-muted">Add an elderly parent to keep their profile and consent together.</p>
          </div>
        ) : null}
      </div>
    </>
  );
}
