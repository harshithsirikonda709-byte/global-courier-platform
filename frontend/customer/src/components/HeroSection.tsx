'use client';

import React from 'react';
import {
  ArrowRight,
  Search,
  ShieldCheck,
  PlaneTakeoff,
  Home,
  Package,
  MapPin,
  CheckCircle2,
  Sparkles,
  Clock,
} from 'lucide-react';

export default function HeroSection() {
  return (
    <section
      id="home"
      className="relative overflow-hidden bg-white pt-10 pb-20 lg:pt-16 lg:pb-28 border-b border-slate-100"
    >
      {/* Subtle architectural grid & ambient glow */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:24px_24px] opacity-40"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-32 right-0 w-[38rem] h-[38rem] rounded-full bg-gradient-to-br from-orange-100/60 via-blue-50/40 to-transparent blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute bottom-0 -left-24 w-[28rem] h-[28rem] rounded-full bg-gradient-to-tr from-slate-100 via-blue-50/50 to-transparent blur-3xl"
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-10 items-center">
          {/* Left Column: Hero Messaging & CTAs */}
          <div className="lg:col-span-6 space-y-8">
            {/* Trust Badge */}
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-slate-100 border border-slate-200/90 text-[#0B1F3A] text-xs sm:text-sm font-semibold">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-orange-500 text-white">
                <Sparkles className="w-3 h-3" />
              </span>
              <span>Built for Indian Families Sending Care Packages Abroad</span>
            </div>

            {/* Required Headline */}
            <h1 className="text-4xl sm:text-5xl xl:text-[3.4rem] font-extrabold tracking-tight text-[#0B1F3A] leading-[1.12]">
              Send Love From India.{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0B1F3A] via-[#1E3A8A] to-orange-600">
                We&apos;ll Deliver It Worldwide.
              </span>
            </h1>

            {/* Supporting Text */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl">
              From festival clothes and student essentials to Mom&apos;s permitted
              homemade snacks and family gifts—we pick up right from your
              doorstep in India, handle export-grade packing and customs
              documentation, and deliver safely to your loved ones overseas.
            </p>

            {/* Primary & Secondary CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-1">
              <a
                href="#book-courier"
                className="inline-flex items-center justify-center gap-2.5 px-7 py-4 rounded-xl text-base font-bold text-white bg-orange-600 hover:bg-orange-500 shadow-lg shadow-orange-600/20 hover:shadow-xl hover:shadow-orange-600/25 transition-all group"
              >
                <span>Book a Pickup</span>
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </a>

              <a
                href="#track-shipment"
                className="inline-flex items-center justify-center gap-2.5 px-7 py-4 rounded-xl text-base font-bold text-[#0B1F3A] bg-white hover:bg-slate-50 border-2 border-[#0B1F3A]/15 hover:border-[#0B1F3A]/35 transition-all"
              >
                <Search className="w-4 h-4 text-orange-600" />
                <span>Track Shipment</span>
              </a>
            </div>

            {/* Key Highlights Bar */}
            <div className="pt-4 border-t border-slate-200/80 grid grid-cols-3 gap-4 sm:gap-6">
              <div>
                <div className="flex items-center gap-1.5 text-[#0B1F3A] font-extrabold text-lg sm:text-xl">
                  <Home className="w-4 h-4 text-orange-600 shrink-0" />
                  <span>Doorstep</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                  Home pickup across India
                </p>
              </div>

              <div>
                <div className="flex items-center gap-1.5 text-[#0B1F3A] font-extrabold text-lg sm:text-xl">
                  <ShieldCheck className="w-4 h-4 text-orange-600 shrink-0" />
                  <span>5-Ply Box</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                  Vacuum &amp; export packing
                </p>
              </div>

              <div>
                <div className="flex items-center gap-1.5 text-[#0B1F3A] font-extrabold text-lg sm:text-xl">
                  <Clock className="w-4 h-4 text-orange-600 shrink-0" />
                  <span>3–7 Days</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                  Express global air transit
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: International Parcel Logistics Illustration */}
          <div className="lg:col-span-6">
            <div className="relative mx-auto max-w-xl lg:max-w-none">
              {/* Main Navy Logistics Command Card */}
              <div className="relative rounded-3xl bg-gradient-to-br from-[#0B1F3A] via-[#102A4C] to-[#0A192F] p-6 sm:p-8 text-white shadow-2xl shadow-[#0B1F3A]/20 border border-slate-700/60 overflow-hidden">
                {/* Decorative radar rings */}
                <svg
                  aria-hidden="true"
                  className="absolute inset-0 w-full h-full opacity-20 pointer-events-none"
                  viewBox="0 0 600 450"
                  fill="none"
                >
                  <circle
                    cx="120"
                    cy="250"
                    r="90"
                    stroke="#38BDF8"
                    strokeDasharray="4 4"
                  />
                  <circle
                    cx="120"
                    cy="250"
                    r="160"
                    stroke="#38BDF8"
                    strokeDasharray="6 6"
                  />
                  <circle
                    cx="470"
                    cy="150"
                    r="110"
                    stroke="#F97316"
                    strokeDasharray="4 4"
                  />
                </svg>

                {/* Header of Logistics Visual */}
                <div className="relative z-10 flex items-center justify-between pb-6 border-b border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-400/30 flex items-center justify-center">
                      <PlaneTakeoff className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-wider text-slate-300 font-semibold">
                        International Air Corridor
                      </p>
                      <p className="text-sm font-bold text-white">
                        India Doorstep → Global Destinations
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    Customs Guided
                  </span>
                </div>

                {/* Interactive SVG Air Route Map */}
                <div className="relative z-10 my-6 bg-white/5 rounded-2xl p-4 sm:p-5 border border-white/10">
                  <svg
                    viewBox="0 0 520 200"
                    className="w-full h-auto"
                    role="img"
                    aria-label="Illustration of parcel pickup in India flying across international air routes to global family destinations"
                  >
                    <defs>
                      <linearGradient
                        id="routeGrad"
                        x1="0%"
                        y1="100%"
                        x2="100%"
                        y2="0%"
                      >
                        <stop offset="0%" stopColor="#F97316" />
                        <stop offset="50%" stopColor="#FBBF24" />
                        <stop offset="100%" stopColor="#38BDF8" />
                      </linearGradient>
                    </defs>

                    {/* Background world latitude lines */}
                    <line
                      x1="20"
                      y1="50"
                      x2="500"
                      y2="50"
                      stroke="rgba(255,255,255,0.07)"
                      strokeWidth="1"
                    />
                    <line
                      x1="20"
                      y1="100"
                      x2="500"
                      y2="100"
                      stroke="rgba(255,255,255,0.07)"
                      strokeWidth="1"
                    />
                    <line
                      x1="20"
                      y1="150"
                      x2="500"
                      y2="150"
                      stroke="rgba(255,255,255,0.07)"
                      strokeWidth="1"
                    />

                    {/* Primary Flight Arcs from India Hub (x:95, y:145) */}
                    <path
                      d="M 95 145 Q 250 15 435 55"
                      fill="none"
                      stroke="url(#routeGrad)"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                    <path
                      d="M 95 145 Q 260 65 450 115"
                      fill="none"
                      stroke="url(#routeGrad)"
                      strokeWidth="2"
                      strokeDasharray="5 5"
                    />
                    <path
                      d="M 95 145 Q 240 120 410 165"
                      fill="none"
                      stroke="rgba(249,115,22,0.55)"
                      strokeWidth="2"
                      strokeDasharray="4 4"
                    />

                    {/* Origin Node: India Home Pickup */}
                    <g transform="translate(95, 145)">
                      <circle r="22" fill="rgba(249,115,22,0.18)" />
                      <circle
                        r="12"
                        fill="#F97316"
                        stroke="#FFFFFF"
                        strokeWidth="2.5"
                      />
                      <text
                        x="0"
                        y="36"
                        textAnchor="middle"
                        fill="#F8FAFC"
                        fontSize="11"
                        fontWeight="700"
                      >
                        INDIA PICKUP
                      </text>
                    </g>

                    {/* Mid-Flight Verification Node */}
                    <g transform="translate(260, 62)">
                      <rect
                        x="-54"
                        y="-16"
                        width="108"
                        height="28"
                        rx="14"
                        fill="#0F2942"
                        stroke="#F97316"
                        strokeWidth="1.5"
                      />
                      <text
                        x="0"
                        y="2"
                        textAnchor="middle"
                        fill="#FDBA74"
                        fontSize="10"
                        fontWeight="700"
                      >
                        ✈ PRIORITY AIR
                      </text>
                    </g>

                    {/* Destination 1: North America / UK */}
                    <g transform="translate(435, 55)">
                      <circle r="16" fill="rgba(56,189,248,0.2)" />
                      <circle
                        r="8"
                        fill="#38BDF8"
                        stroke="#FFFFFF"
                        strokeWidth="2"
                      />
                      <text
                        x="0"
                        y="-16"
                        textAnchor="middle"
                        fill="#E2E8F0"
                        fontSize="10"
                        fontWeight="700"
                      >
                        USA • UK • CANADA
                      </text>
                    </g>

                    {/* Destination 2: Europe & UAE */}
                    <g transform="translate(450, 115)">
                      <circle r="7" fill="#38BDF8" />
                      <text
                        x="-12"
                        y="4"
                        textAnchor="end"
                        fill="#CBD5E1"
                        fontSize="10"
                        fontWeight="600"
                      >
                        UAE • EUROPE
                      </text>
                    </g>

                    {/* Destination 3: Australia & Singapore */}
                    <g transform="translate(410, 165)">
                      <circle r="7" fill="#F97316" />
                      <text
                        x="-12"
                        y="4"
                        textAnchor="end"
                        fill="#CBD5E1"
                        fontSize="10"
                        fontWeight="600"
                      >
                        AUSTRALIA • SG
                      </text>
                    </g>
                  </svg>

                  {/* Destination Country Pills */}
                  <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-300">
                    <span className="font-medium text-slate-400">
                      Top Family Corridors:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {['USA', 'UK', 'Canada', 'Australia', 'UAE', 'Germany'].map(
                        (country) => (
                          <span
                            key={country}
                            className="px-2.5 py-0.5 rounded-md bg-white/10 text-white font-semibold"
                          >
                            {country}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                </div>

                {/* Parcel Journey Stages Inside Card */}
                <div className="relative z-10 grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="rounded-xl bg-white/10 p-3.5 border border-white/10">
                    <div className="flex items-center gap-2 text-orange-400 text-xs font-bold uppercase">
                      <MapPin className="w-4 h-4" />
                      <span>Step 1 • India</span>
                    </div>
                    <p className="text-sm font-bold text-white mt-1">
                      Home Collection
                    </p>
                    <p className="text-xs text-slate-300 mt-0.5">
                      Driver collects from parents&apos; doorstep
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/10 p-3.5 border border-white/10">
                    <div className="flex items-center gap-2 text-sky-400 text-xs font-bold uppercase">
                      <Package className="w-4 h-4" />
                      <span>Step 2 • Hub</span>
                    </div>
                    <p className="text-sm font-bold text-white mt-1">
                      Vacuum &amp; 5-Ply Pack
                    </p>
                    <p className="text-xs text-slate-300 mt-0.5">
                      Customs check &amp; export boxing
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/10 p-3.5 border border-white/10">
                    <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Step 3 • Abroad</span>
                    </div>
                    <p className="text-sm font-bold text-white mt-1">
                      Global Delivery
                    </p>
                    <p className="text-xs text-slate-300 mt-0.5">
                      Handed to family overseas
                    </p>
                  </div>
                </div>
              </div>

              {/* Floating Badge: Permitted Items Care */}
              <div className="mt-4 sm:mt-0 sm:absolute sm:-bottom-6 sm:left-6 bg-white rounded-2xl p-4 shadow-xl border border-slate-200/90 flex items-center gap-3.5 max-w-xs">
                <div className="w-11 h-11 rounded-xl bg-orange-50 border border-orange-200 flex items-center justify-center shrink-0">
                  <Package className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-orange-600">
                    Care Package Specialists
                  </p>
                  <p className="text-xs font-semibold text-slate-700 mt-0.5">
                    Clothes, Homemade Snacks, Pickles, Spices &amp; Documents
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

