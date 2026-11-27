"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Suspense } from "react";
import { useEffect, useState } from "react";
import ParentForm from "@/components/ParentForm";
import { api, type ParentInput, type ParentProfile } from "@/lib/api";

function EditParentContent() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [parent, setParent] = useState<ParentProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<ParentProfile>(`/v1/carecircle/parents/${params.id}`)
      .then(setParent)
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Unable to load parent."));
  }, [params.id]);

  async function update(payload: ParentInput) {
    const updated = await api<ParentProfile>(`/v1/carecircle/parents/${params.id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    setParent(updated);
    router.push(`/family/parents/${updated.id}`);
  }

  if (!parent) {
    return (
      <>
        {error ? <div className="cc-alert error" role="alert">{error}</div> : <p className="cc-muted">Loading parent profile...</p>}
      </>
    );
  }

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>Update {parent.full_name}</h1>
          <p className="cc-muted">Changes are written to the CareCircle database.</p>
        </div>
        <Link className="cc-button secondary" href={`/family/parents/${parent.id}`}>Cancel</Link>
      </div>
      <ParentForm initial={parent} submittingLabel="Save changes" onSubmit={update} />
    </>
  );
}

export default function EditParentPage() {
  return (
    <Suspense fallback={<p className="cc-muted">Loading parent profile...</p>}>
      <EditParentContent />
    </Suspense>
  );
}
