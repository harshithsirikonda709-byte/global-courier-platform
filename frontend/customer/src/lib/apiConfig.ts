/**
 * Frontend Architecture Configuration for FastAPI & Supabase Integration
 *
 * No dummy API calls are performed in this phase.
 * Once the FastAPI backend and Supabase project are connected, configure
 * NEXT_PUBLIC_FASTAPI_BASE_URL, NEXT_PUBLIC_SUPABASE_URL, and
 * NEXT_PUBLIC_SUPABASE_ANON_KEY in `.env.local`.
 */

export interface PlatformEnvironmentConfig {
  fastApiBaseUrl: string | null;
  supabaseUrl: string | null;
  supabaseAnonKey: string | null;
  isBackendConfigured: boolean;
}

export function getPlatformEnvironmentConfig(): PlatformEnvironmentConfig {
  const fastApiBaseUrl = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || null;
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || null;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || null;

  return {
    fastApiBaseUrl,
    supabaseUrl,
    supabaseAnonKey,
    isBackendConfigured: Boolean(fastApiBaseUrl && supabaseUrl && supabaseAnonKey),
  };
}

export const FASTAPI_ENDPOINTS = {
  bookings: '/api/v1/bookings',
  trackShipment: (trackingNumber: string) =>
    `/api/v1/shipments/track/${encodeURIComponent(trackingNumber)}`,
  authProfile: '/api/v1/customers/me',
} as const;

