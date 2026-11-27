export type AuthUser = {
  id: string;
  full_name: string;
  email: string;
  phone?: string | null;
  account_type: "family" | "companion" | "parent";
  is_admin: boolean;
};

export type EmergencyContact = {
  id?: string;
  full_name: string;
  relationship?: string | null;
  phone: string;
  alternate_phone?: string | null;
  is_primary: boolean;
};

export type Consent = {
  id: string;
  status: "active" | "family_reported" | "superseded" | "withdrawn";
  consent_source: "parent" | "family_reported";
  scope: string;
  consent_text: string;
  signer_relationship?: string | null;
  effective_at?: string | null;
  expires_at?: string | null;
  withdrawn_at?: string | null;
  withdrawal_reason?: string | null;
};

export type AuthSession = {
  access_token: string;
  refresh_token?: string | null;
  expires_in?: number | null;
  user: AuthUser;
};

export type ConfirmationPending = {
  confirmation_required: true;
  message: string;
  user_id?: string;
  email: string;
};

export type ParentProfile = {
  id: string;
  full_name: string;
  date_of_birth?: string | null;
  gender?: string | null;
  phone?: string | null;
  alternate_phone?: string | null;
  address_line1: string;
  address_line2?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  address_instructions?: string | null;
  preferred_language: string;
  interests?: string | null;
  accessibility_preferences?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  emergency_contacts: EmergencyContact[];
  consents: Consent[];
};

export type ParentInput = {
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  alternate_phone?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  address_instructions?: string;
  preferred_language: string;
  interests?: string;
  accessibility_preferences?: string;
  relationship?: string;
  emergency_contacts: EmergencyContact[];
};

export type CompanionProfile = {
  id: string;
  user_id?: string;
  display_name: string;
  bio: string;
  languages: string[];
  service_area: string;
  timezone_name: string;
  identity_document_type: string;
  identity_status: string;
  approval_status: string;
  admin_notes?: string | null;
  email?: string;
  phone?: string | null;
};

export type Availability = {
  id?: string;
  weekday: number;
  start_time: string;
  end_time: string;
};

export type Visit = {
  id: string;
  parent_id: string;
  family_id: string;
  booked_by_user_id: string;
  companion_id?: string | null;
  scheduled_start: string;
  duration_minutes: number;
  requirements?: string | null;
  status: "requested" | "assigned" | "accepted" | "in_progress" | "completed" | "cancelled";
  rejection_reason?: string | null;
  cancellation_reason?: string | null;
  assigned_at?: string | null;
  checked_in_at?: string | null;
  checked_out_at?: string | null;
};

const TOKEN_KEY = "carecircle_access_token";
const USER_KEY = "carecircle_user";

export function saveAuth(token: string, user: AuthUser) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getStoredUser(): AuthUser | null {
  const value = localStorage.getItem(USER_KEY);
  if (!value) return null;
  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    return null;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`/api${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = "The request could not be completed.";
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
      if (Array.isArray(body.detail)) {
        detail = body.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(". ");
      }
    } catch {
      detail = `Request failed (${response.status})`;
    }
    throw new Error(detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
