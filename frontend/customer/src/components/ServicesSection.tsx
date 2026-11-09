'use client';

import React from 'react';
import {
  Shirt,
  UtensilsCrossed,
  Gift,
  FileText,
  Check,
  ShieldAlert,
  ArrowUpRight,
} from 'lucide-react';
import { SERVICE_ITEMS } from '@/data/courierData';
import { ParcelCategory } from '@/types/courier';

interface ServicesSectionProps {
  onSelectCategoryForBooking: (category: ParcelCategory) => void;
}

const SERVICE_ICONS: Record<ParcelCategory, React.ElementType> = {
  clothes_personal: Shirt,
  homemade_food: UtensilsCrossed,
  gifts_family: Gift,
  documents: FileText,
};

export default function ServicesSection({
  onSelectCategoryForBooking,
}: ServicesSectionProps) {
  return (
    <section
      id="services"
      className="py-20 lg:py-28 bg-slate-50 border-b border-slate-200/80 scroll-mt-20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-50 border border-orange-200 text-orange-700 text-xs font-bold uppercase tracking-wider">
            What You Can Ship
          </span>
          <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold text-[#0B1F3A] tracking-tight">
            Specialized International Parcel Services
          </h2>
          <p className="mt-3 text-base sm:text-lg text-slate-600">
            Tailored for Indian households sending clothes, homemade delicacies,
            celebration gifts, and official documents to relatives and students
            abroad.
          </p>
        </div>

        {/* 4 Service Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {SERVICE_ITEMS.map((service) => {
            const IconComponent = SERVICE_ICONS[service.id] || Shirt;
            return (
              <div
                key={service.id}
                className="group bg-white rounded-3xl p-7 sm:p-8 shadow-lg shadow-slate-900/5 border border-slate-200/90 hover:border-[#0B1F3A]/30 transition-all flex flex-col justify-between"
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-[#0B1F3A] text-orange-400 flex items-center justify-center shadow-md shadow-[#0B1F3A]/15 shrink-0">
                      <IconComponent className="w-7 h-7" />
                    </div>
                    <a
                      href="#book-courier"
                      onClick={() => onSelectCategoryForBooking(service.id)}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-[#0B1F3A] bg-slate-100 hover:bg-orange-600 hover:text-white transition-colors"
                    >
                      <span>Book This Category</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </a>
                  </div>

                  {/* Title & Subtitle */}
                  <div className="mt-6">
                    <p className="text-xs font-bold uppercase tracking-wider text-orange-600">
                      {service.subtitle}
                    </p>
                    <h3 className="mt-1 text-xl sm:text-2xl font-extrabold text-[#0B1F3A]">
                      {service.title}
                    </h3>
                    <p className="mt-3 text-sm sm:text-base text-slate-600 leading-relaxed">
                      {service.description}
                    </p>
                  </div>

                  {/* Common Items List */}
                  <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {service.examples.map((example) => (
                      <div
                        key={example}
                        className="flex items-center gap-2 text-xs sm:text-sm font-medium text-slate-700 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200/60"
                      >
                        <Check className="w-4 h-4 text-orange-600 shrink-0" />
                        <span>{example}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Regulation Note Footer */}
                <div className="mt-6 pt-4 border-t border-slate-100 flex items-start gap-2 text-xs text-slate-500">
                  <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <span>{service.regulationNote}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Mandatory Destination-Country Regulations Advisory Banner */}
        <div className="mt-12 rounded-3xl bg-gradient-to-r from-[#0B1F3A] via-[#122C50] to-[#0B1F3A] p-7 sm:p-9 text-white shadow-xl border border-slate-700">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start gap-4 max-w-3xl">
              <div className="w-12 h-12 rounded-2xl bg-orange-500/20 border border-orange-400/40 flex items-center justify-center shrink-0 mt-0.5">
                <ShieldAlert className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <span className="inline-block text-xs font-bold uppercase tracking-wider text-orange-400">
                  International Customs &amp; Biosecurity Compliance
                </span>
                <h3 className="mt-1 text-lg sm:text-xl font-extrabold text-white">
                  Item Acceptance Depends on Destination-Country Regulations
                </h3>
                <p className="mt-2 text-sm text-slate-300 leading-relaxed">
                  Every destination country enforces specific import,
                  agricultural, and biosecurity rules (such as US FDA, UK DEFRA,
                  Australia DAFF, and EU Customs). While dry homemade foods,
                  spices, garments, and personal gifts are widely permitted,
                  perishable dairy/meat items, seeds, unsealed liquids, and
                  restricted goods may be declined during doorstep verification
                  to protect your parcel from customs seizure.
                </p>
              </div>
            </div>

            <div className="shrink-0">
              <a
                href="#book-courier"
                className="inline-flex items-center justify-center px-6 py-3.5 rounded-xl text-sm font-bold text-[#0B1F3A] bg-white hover:bg-orange-50 transition-colors"
              >
                Check Country Rules in Form
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

