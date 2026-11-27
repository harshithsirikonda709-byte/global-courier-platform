"use client";

import { useRouter } from "next/navigation";
import ParentForm from "@/components/ParentForm";
import { api, type ParentInput, type ParentProfile } from "@/lib/api";

export default function NewParentPage() {
  const router = useRouter();

  async function create(payload: ParentInput) {
    const parent = await api<ParentProfile>("/v1/carecircle/parents", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    router.push(`/family/parents/${parent.id}`);
  }

  return (
    <>
      <div className="cc-page-header">
        <div>
          <h1>Add Parent Profile</h1>
          <p className="cc-muted">Store contact, address, language and activity preferences.</p>
        </div>
      </div>
      <ParentForm submittingLabel="Save parent profile" onSubmit={create} />
    </>
  );
}
