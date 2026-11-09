'use client';

import React, { useState } from 'react';
import {
  Search,
  PackageSearch,
  AlertCircle,
  Info,
  RotateCcw,
  Radio,
} from 'lucide-react';
import { validateTrackingNumber } from '@/lib/validation';
import { FASTAPI_ENDPOINTS } from '@/lib/apiConfig';

export default function ShipmentTrackingSection() {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [queriedTrackingNumber, setQueriedTrackingNumber] = useState<
    string | null
  >(null);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const validationError = validateTrackingNumber(trackingNumber);

    if (validationError) {
      setError(validationError);
      setQueriedTrackingNumber(null);
      return;
    }

    setError(null);
    setQueriedTrackingNumber(trackingNumber.trim().toUpperCase());
  };

  return (
    <section
      id="track-shipment"
      className="py-20 lg:py-28 bg-white border-b border-slate-100 scroll-mt-20"
    >
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-gradient-to-br from-[#0B1F3A] via-[#10294B] to-[#0A192F] p-8 sm:p-12 text-white shadow-2xl shadow-[#0B1F3A]/15 border border-slate-700/70 relative overflow-hidden">
          {/* Decorative glow */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -top-24 -right-24 w-72 h-72 rounded-full bg-orange-500/15 blur-3xl"
          />

          <div className="relative z-10 max-w-2xl mx-auto text-center">
            <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/15 text-orange-300 text-xs font-bold uppercase tracking-wider">
              <Radio className="w-3.5 h-3.5 text-orange-400" />
              Global Shipment Tracker
            </span>

            <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Track Your International Parcel
            </h2>
            <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed">
              Enter your Global Courier Airway Bill (AWB) or Booking Reference
              Number to check milestone updates from home collection in India to
              delivery abroad.
            </p>
          </div>

          {/* Tracking Input & Button Form */}
          <form
            onSubmit={handleSubmit}
            noValidate
            className="relative z-10 mt-8 max-w-2xl mx-auto"
          >
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <PackageSearch className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="trackingNumber"
                  name="trackingNumber"
                  type="text"
                  value={trackingNumber}
                  onChange={(e) => {
                    setTrackingNumber(e.target.value);
                    if (error) setError(null);
                    if (queriedTrackingNumber) setQueriedTrackingNumber(null);
                  }}
                  placeholder="Enter Tracking Number (e.g., GCP-2026-84920)"
                  aria-label="Shipment Tracking Number"
                  aria-invalid={Boolean(error)}
                  className={`w-full pl-12 pr-4 py-4 rounded-2xl bg-white text-slate-900 placeholder:text-slate-400 text-sm sm:text-base font-medium focus:outline-none focus:ring-2 transition-all ${
                    error
                      ? 'ring-2 ring-red-400'
                      : 'focus:ring-orange-400 border border-white/20'
                  }`}
                />
              </div>

              <button
                type="submit"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-2xl text-base font-bold text-white bg-orange-600 hover:bg-orange-500 shadow-lg shadow-orange-600/25 transition-all shrink-0 cursor-pointer"
              >
                <Search className="w-5 h-5" />
                <span>Track Shipment</span>
              </button>
            </div>

            {/* Validation Error */}
            {error && (
              <div
                role="alert"
                className="mt-3 flex items-center gap-2 text-xs sm:text-sm text-red-300 bg-red-950/60 border border-red-400/40 rounded-xl px-4 py-2.5"
              >
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Honest Backend Readiness Status (No Fake Tracking Data) */}
            {queriedTrackingNumber && (
              <div
                role="status"
                aria-live="polite"
                className="mt-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 p-5 text-left space-y-3"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-400/30">
                          {queriedTrackingNumber}
                        </span>
                        <span className="text-xs font-semibold text-amber-300">
                          • Live Tracking Backend Not Connected
                        </span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-200 mt-2 leading-relaxed">
                        Your tracking number format has been validated. Live
                        milestone lookup is currently unavailable because the
                        FastAPI endpoint (
                        <code className="text-xs bg-black/30 px-1.5 py-0.5 rounded text-orange-200">
                          GET{' '}
                          {FASTAPI_ENDPOINTS.trackShipment(
                            queriedTrackingNumber
                          )}
                        </code>
                        ) and Supabase shipment events table are not yet
                        connected in this initial frontend release.
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setTrackingNumber('');
                      setQueriedTrackingNumber(null);
                    }}
                    className="text-xs text-slate-300 hover:text-white inline-flex items-center gap-1 shrink-0 cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Reset
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Tracking Stages Legend */}
          <div className="relative z-10 mt-10 pt-6 border-t border-white/10 grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
            {[
              '1. Pickup Scheduled',
              '2. Collected at Home',
              '3. Hub Verified & Packed',
              '4. In Air Transit',
              '5. Delivered Abroad',
            ].map((stage) => (
              <div
                key={stage}
                className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-slate-300"
              >
                {stage}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

