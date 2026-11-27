"use client";

import { useState } from "react";
import type { ParentInput, ParentProfile } from "@/lib/api";

type Props = {
  initial?: ParentProfile;
  submittingLabel: string;
  onSubmit: (payload: ParentInput) => Promise<void>;
};

function emptyContact() {
  return {
    full_name: "",
    relationship: "",
    phone: "",
    alternate_phone: "",
    is_primary: false,
  };
}

export default function ParentForm({ initial, submittingLabel, onSubmit }: Props) {
  const [form, setForm] = useState<ParentInput>({
    full_name: initial?.full_name ?? "",
    date_of_birth: initial?.date_of_birth ?? "",
    gender: initial?.gender ?? "",
    phone: initial?.phone ?? "",
    alternate_phone: initial?.alternate_phone ?? "",
    address_line1: initial?.address_line1 ?? "",
    address_line2: initial?.address_line2 ?? "",
    city: initial?.city ?? "",
    state: initial?.state ?? "",
    postal_code: initial?.postal_code ?? "",
    country: initial?.country ?? "India",
    address_instructions: initial?.address_instructions ?? "",
    preferred_language: initial?.preferred_language ?? "",
    interests: initial?.interests ?? "",
    accessibility_preferences: initial?.accessibility_preferences ?? "",
    relationship: "",
    emergency_contacts: initial?.emergency_contacts?.length
      ? initial.emergency_contacts.map((contact) => ({
          full_name: contact.full_name,
          relationship: contact.relationship ?? "",
          phone: contact.phone,
          alternate_phone: contact.alternate_phone ?? "",
          is_primary: contact.is_primary,
        }))
      : [{ ...emptyContact(), is_primary: true }],
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function setField<K extends keyof ParentInput>(key: K, value: ParentInput[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function setContact(index: number, key: "full_name" | "relationship" | "phone" | "alternate_phone" | "is_primary", value: string | boolean) {
    setForm((current) => ({
      ...current,
      emergency_contacts: current.emergency_contacts.map((contact, contactIndex) =>
        contactIndex === index ? { ...contact, [key]: value } : contact
      ),
    }));
  }

  function validate() {
    if (form.full_name.trim().length < 2) return "Enter the parent’s full name.";
    if (form.address_line1.trim().length < 5) return "Enter a complete residential address.";
    if (form.city.trim().length < 2) return "Enter the city.";
    if (form.state.trim().length < 2) return "Enter the state.";
    if (form.postal_code.trim().length < 3) return "Enter a valid postal code.";
    if (form.preferred_language.trim().length < 2) return "Enter a preferred language.";
    for (const contact of form.emergency_contacts) {
      if (contact.full_name.trim().length < 2) return "Enter a name for every emergency contact.";
      if (contact.phone.trim().length < 7) return "Enter a valid emergency contact phone number.";
    }
    return "";
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        ...form,
        date_of_birth: form.date_of_birth || undefined,
        gender: form.gender || undefined,
        phone: form.phone || undefined,
        alternate_phone: form.alternate_phone || undefined,
        address_line2: form.address_line2 || undefined,
        address_instructions: form.address_instructions || undefined,
        interests: form.interests || undefined,
        accessibility_preferences: form.accessibility_preferences || undefined,
        emergency_contacts: form.emergency_contacts.map((contact, index) => ({
          ...contact,
          relationship: contact.relationship || undefined,
          alternate_phone: contact.alternate_phone || undefined,
          is_primary: index === 0 ? true : contact.is_primary,
        })),
      });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to save the parent profile.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={submit} noValidate>
      {error ? <div className="cc-alert error" role="alert">{error}</div> : null}

      <div className="cc-card cc-card-pad">
        <h2>Personal Information</h2>
        <div className="cc-grid cc-grid-two">
          <div className="cc-field">
            <label htmlFor="full_name">Full name *</label>
            <input id="full_name" value={form.full_name} onChange={(event) => setField("full_name", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="date_of_birth">Date of birth</label>
            <input id="date_of_birth" type="date" value={form.date_of_birth ?? ""} onChange={(event) => setField("date_of_birth", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="gender">Gender, if volunteered</label>
            <select id="gender" value={form.gender ?? ""} onChange={(event) => setField("gender", event.target.value)}>
              <option value="">Prefer not to say</option>
              <option value="Female">Female</option>
              <option value="Male">Male</option>
              <option value="Non-binary">Non-binary</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="cc-field">
            <label htmlFor="preferred_language">Preferred language *</label>
            <input id="preferred_language" value={form.preferred_language} onChange={(event) => setField("preferred_language", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="phone">Phone</label>
            <input id="phone" value={form.phone ?? ""} onChange={(event) => setField("phone", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="alternate_phone">Alternate phone</label>
            <input id="alternate_phone" value={form.alternate_phone ?? ""} onChange={(event) => setField("alternate_phone", event.target.value)} />
          </div>
        </div>
      </div>

      <div className="cc-card cc-card-pad" style={{ marginTop: 20 }}>
        <h2>Address</h2>
        <div className="cc-grid cc-grid-two">
          <div className="cc-field">
            <label htmlFor="address_line1">Address line 1 *</label>
            <input id="address_line1" value={form.address_line1} onChange={(event) => setField("address_line1", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="address_line2">Address line 2</label>
            <input id="address_line2" value={form.address_line2 ?? ""} onChange={(event) => setField("address_line2", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="city">City *</label>
            <input id="city" value={form.city} onChange={(event) => setField("city", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="state">State *</label>
            <input id="state" value={form.state} onChange={(event) => setField("state", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="postal_code">Postal code *</label>
            <input id="postal_code" value={form.postal_code} onChange={(event) => setField("postal_code", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="country">Country *</label>
            <input id="country" value={form.country} onChange={(event) => setField("country", event.target.value)} />
          </div>
        </div>
        <div className="cc-field">
          <label htmlFor="address_instructions">Address or entry instructions</label>
          <textarea id="address_instructions" value={form.address_instructions ?? ""} onChange={(event) => setField("address_instructions", event.target.value)} />
        </div>
      </div>

      <div className="cc-card cc-card-pad" style={{ marginTop: 20 }}>
        <h2>Preferences</h2>
        <div className="cc-grid cc-grid-two">
          <div className="cc-field">
            <label htmlFor="interests">Interests and hobbies</label>
            <textarea id="interests" value={form.interests ?? ""} onChange={(event) => setField("interests", event.target.value)} />
          </div>
          <div className="cc-field">
            <label htmlFor="accessibility_preferences">Accessibility preferences</label>
            <textarea id="accessibility_preferences" value={form.accessibility_preferences ?? ""} onChange={(event) => setField("accessibility_preferences", event.target.value)} />
          </div>
        </div>
      </div>

      <div className="cc-card cc-card-pad" style={{ marginTop: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <h2>Emergency Contacts</h2>
          <button
            type="button"
            className="cc-button secondary"
            onClick={() => setForm((current) => ({
              ...current,
              emergency_contacts: [...current.emergency_contacts, emptyContact()],
            }))}
          >
            Add contact
          </button>
        </div>

        {form.emergency_contacts.map((contact, index) => (
          <div key={index} className="cc-grid cc-grid-two" style={{ borderTop: index ? "1px solid #e5e9f2" : undefined, paddingTop: index ? 18 : 0, marginTop: 12 }}>
            <div className="cc-field">
              <label htmlFor={`contact_name_${index}`}>Contact name *</label>
              <input id={`contact_name_${index}`} value={contact.full_name} onChange={(event) => setContact(index, "full_name", event.target.value)} />
            </div>
            <div className="cc-field">
              <label htmlFor={`contact_relationship_${index}`}>Relationship</label>
              <input id={`contact_relationship_${index}`} value={contact.relationship ?? ""} onChange={(event) => setContact(index, "relationship", event.target.value)} />
            </div>
            <div className="cc-field">
              <label htmlFor={`contact_phone_${index}`}>Phone *</label>
              <input id={`contact_phone_${index}`} value={contact.phone} onChange={(event) => setContact(index, "phone", event.target.value)} />
            </div>
            <div className="cc-field">
              <label htmlFor={`contact_alternate_${index}`}>Alternate phone</label>
              <input id={`contact_alternate_${index}`} value={contact.alternate_phone ?? ""} onChange={(event) => setContact(index, "alternate_phone", event.target.value)} />
            </div>
            {form.emergency_contacts.length > 1 ? (
              <button
                type="button"
                className="cc-button danger"
                style={{ width: "fit-content" }}
                onClick={() => setForm((current) => ({
                  ...current,
                  emergency_contacts: current.emergency_contacts.filter((_, contactIndex) => contactIndex !== index),
                }))}
              >
                Remove
              </button>
            ) : null}
          </div>
        ))}
      </div>

      <div className="cc-actions" style={{ marginTop: 20 }}>
        <button type="submit" className="cc-button" disabled={submitting}>
          {submitting ? "Saving..." : submittingLabel}
        </button>
      </div>
    </form>
  );
}
