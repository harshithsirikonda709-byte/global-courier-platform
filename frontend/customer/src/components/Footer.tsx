import React from 'react';
import {
  Globe,
  PackageCheck,
  Phone,
  Mail,
  MapPin,
  Clock,
  ShieldCheck,
} from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#0B1F3A] text-slate-300 border-t border-slate-800">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10 lg:gap-8">
          {/* Column 1: Company Information */}
          <div className="lg:col-span-4 space-y-5">
            <a href="#home" className="inline-flex items-center gap-3">
              <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-white/10 text-white border border-white/15">
                <Globe className="w-6 h-6 text-orange-400" />
                <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-orange-500 flex items-center justify-center">
                  <PackageCheck className="w-2.5 h-2.5 text-white" />
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-extrabold tracking-tight text-white leading-none">
                  GLOBAL <span className="text-orange-400">COURIER</span>
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400 mt-1">
                  India to World Logistics
                </span>
              </div>
            </a>

            <p className="text-sm text-slate-300 leading-relaxed max-w-sm">
              Helping Indian families send clothes, permitted homemade food
              products, festival gifts, and personal belongings from their
              doorstep in India to family members living abroad.
            </p>

            <div className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-slate-200">
              <ShieldCheck className="w-4 h-4 text-orange-400 shrink-0" />
              <span>Export-Grade Packing &amp; Customs Documentation</span>
            </div>
          </div>

          {/* Column 2: Services */}
          <div className="lg:col-span-3 space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
              International Services
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a
                  href="#services"
                  className="hover:text-orange-400 transition-colors"
                >
                  Clothes &amp; Personal Belongings
                </a>
              </li>
              <li>
                <a
                  href="#services"
                  className="hover:text-orange-400 transition-colors"
                >
                  Permitted Homemade Food Products
                </a>
              </li>
              <li>
                <a
                  href="#services"
                  className="hover:text-orange-400 transition-colors"
                >
                  Gifts &amp; Family Packages
                </a>
              </li>
              <li>
                <a
                  href="#services"
                  className="hover:text-orange-400 transition-colors"
                >
                  Express International Documents
                </a>
              </li>
              <li>
                <a
                  href="#book-courier"
                  className="hover:text-orange-400 transition-colors"
                >
                  Doorstep Pickup &amp; Vacuum Packing
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Customer Support & Quick Links */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
              Support &amp; Portal
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a
                  href="#book-courier"
                  className="hover:text-orange-400 transition-colors"
                >
                  Book a Pickup
                </a>
              </li>
              <li>
                <a
                  href="#track-shipment"
                  className="hover:text-orange-400 transition-colors"
                >
                  Track Shipment
                </a>
              </li>
              <li>
                <a
                  href="#how-it-works"
                  className="hover:text-orange-400 transition-colors"
                >
                  How It Works
                </a>
              </li>
              <li>
                <a
                  href="#services"
                  className="hover:text-orange-400 transition-colors"
                >
                  Customs Regulations
                </a>
              </li>
              <li>
                <a
                  href="#book-courier"
                  className="hover:text-orange-400 transition-colors"
                >
                  Prohibited Items Guide
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Contact Details */}
          <div className="lg:col-span-3 space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
              Contact &amp; Operations
            </h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-orange-400 shrink-0 mt-1" />
                <span>
                  International Air Cargo Hub, Andheri East, Mumbai, Maharashtra
                  400099, India
                </span>
              </li>
              <li className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-orange-400 shrink-0" />
                <span>+91 (800) 120-4500 (Toll-Free India)</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-orange-400 shrink-0" />
                <span>support@globalcourier.in</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Clock className="w-4 h-4 text-orange-400 shrink-0" />
                <span>Mon – Sat: 8:00 AM – 9:00 PM IST</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Legal Bar */}
      <div className="border-t border-white/10 bg-[#071529]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>
            © 2026 Global Courier Platform. All rights reserved.
          </p>
          <div className="flex flex-wrap items-center gap-5">
            <a
              href="#services"
              className="hover:text-white transition-colors"
            >
              Terms of Carriage
            </a>
            <a
              href="#services"
              className="hover:text-white transition-colors"
            >
              Privacy Policy
            </a>
            <a
              href="#services"
              className="hover:text-white transition-colors"
            >
              Customs &amp; Export Compliance
            </a>
            <a
              href="#services"
              className="hover:text-white transition-colors"
            >
              Refund &amp; Claims Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

