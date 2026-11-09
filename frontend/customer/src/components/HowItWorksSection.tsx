import React from 'react';
import {
  Laptop,
  Truck,
  PackageCheck,
  Plane,
  Home,
  ArrowRight,
} from 'lucide-react';
import { HOW_IT_WORKS_STEPS } from '@/data/courierData';

const STEP_ICONS = [Laptop, Truck, PackageCheck, Plane, Home];

export default function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="py-20 lg:py-28 bg-white border-b border-slate-100 scroll-mt-20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-[#0B1F3A] text-xs font-bold uppercase tracking-wider">
            End-to-End Logistics Workflow
          </span>
          <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold text-[#0B1F3A] tracking-tight">
            How Global Courier Works
          </h2>
          <p className="mt-3 text-base sm:text-lg text-slate-600">
            A seamless five-step journey from your family&apos;s doorstep in
            India to your loved ones&apos; home abroad.
          </p>
        </div>

        {/* 5-Step Responsive Grid */}
        <div className="relative grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {HOW_IT_WORKS_STEPS.map((step, index) => {
            const IconComponent = STEP_ICONS[index] || PackageCheck;
            return (
              <div
                key={step.stepNumber}
                className="group relative flex flex-col justify-between rounded-3xl bg-slate-50/80 hover:bg-white p-6 border border-slate-200/90 hover:border-orange-300 hover:shadow-xl hover:shadow-[#0B1F3A]/5 transition-all duration-300"
              >
                <div>
                  {/* Top Row: Step Number & Icon */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-[#0B1F3A] text-white flex items-center justify-center shadow-md shadow-[#0B1F3A]/15 group-hover:bg-orange-600 transition-colors">
                      <IconComponent className="w-6 h-6 text-orange-400 group-hover:text-white transition-colors" />
                    </div>
                    <span className="text-2xl font-black text-slate-300 group-hover:text-orange-500/70 transition-colors">
                      {step.stepNumber}
                    </span>
                  </div>

                  {/* Step Title & Description */}
                  <h3 className="text-lg font-extrabold text-[#0B1F3A] leading-snug">
                    {step.title}
                  </h3>
                  <p className="mt-2.5 text-sm text-slate-600 leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Bottom Badge */}
                <div className="mt-6 pt-4 border-t border-slate-200/70 flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[11px] font-bold text-[#0B1F3A]">
                    {step.detailBadge}
                  </span>
                  {index < HOW_IT_WORKS_STEPS.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-slate-400 hidden lg:block group-hover:text-orange-600 group-hover:translate-x-0.5 transition-all" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

