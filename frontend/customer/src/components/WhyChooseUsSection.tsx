import React from 'react';
import {
  Home,
  PackagePlus,
  ReceiptIndianRupee,
  Radar,
  Globe,
  ShieldCheck,
} from 'lucide-react';
import { WHY_CHOOSE_US_FEATURES } from '@/data/courierData';

const FEATURE_ICONS: Record<string, React.ElementType> = {
  'doorstep-pickup': Home,
  'packing-assistance': PackagePlus,
  'transparent-pricing': ReceiptIndianRupee,
  'shipment-tracking': Radar,
  'logistics-partners': Globe,
};

export default function WhyChooseUsSection() {
  return (
    <section className="py-20 lg:py-28 bg-slate-50 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 text-[#0B1F3A] text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5 text-orange-600" />
            The Global Courier Advantage
          </span>
          <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold text-[#0B1F3A] tracking-tight">
            Why Indian Families Trust Us
          </h2>
          <p className="mt-3 text-base sm:text-lg text-slate-600">
            Designed from the ground up to make international parcel shipping
            effortless, safe, and predictable for parents in India and children
            abroad.
          </p>
        </div>

        {/* 5 Feature Cards Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
          {WHY_CHOOSE_US_FEATURES.map((feature, index) => {
            const IconComponent = FEATURE_ICONS[feature.id] || ShieldCheck;
            const colSpanClass =
              index < 3 ? 'lg:col-span-2' : 'lg:col-span-3';

            return (
              <div
                key={feature.id}
                className={`${colSpanClass} group bg-white rounded-3xl p-7 border border-slate-200/90 hover:border-orange-300 shadow-sm hover:shadow-xl hover:shadow-[#0B1F3A]/5 transition-all flex flex-col justify-between`}
              >
                <div>
                  <div className="flex items-center justify-between gap-4 mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-[#0B1F3A] text-orange-400 flex items-center justify-center shadow-md shadow-[#0B1F3A]/15 group-hover:bg-orange-600 group-hover:text-white transition-colors">
                      <IconComponent className="w-6 h-6" />
                    </div>
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-orange-50 text-orange-700 border border-orange-200/80">
                      {feature.metric}
                    </span>
                  </div>

                  <h3 className="text-xl font-extrabold text-[#0B1F3A]">
                    {feature.title}
                  </h3>
                  <p className="mt-2.5 text-sm sm:text-base text-slate-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

