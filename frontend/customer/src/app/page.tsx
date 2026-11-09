'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import HeroSection from '@/components/HeroSection';
import BookingSection from '@/components/BookingSection';
import HowItWorksSection from '@/components/HowItWorksSection';
import ServicesSection from '@/components/ServicesSection';
import ShipmentTrackingSection from '@/components/ShipmentTrackingSection';
import WhyChooseUsSection from '@/components/WhyChooseUsSection';
import Footer from '@/components/Footer';
import AuthReadyModal from '@/components/AuthReadyModal';
import { ParcelCategory } from '@/types/courier';

export default function CustomerPortalHomePage() {
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [preselectedCategory, setPreselectedCategory] = useState<
    ParcelCategory | ''
  >('');

  return (
    <div className="min-h-screen flex flex-col bg-white text-[#0B1F3A]">
      {/* 1. NAVBAR */}
      <Navbar onOpenLoginModal={() => setLoginModalOpen(true)} />

      {/* MAIN CONTENT */}
      <main className="flex-1">
        {/* 2. HERO SECTION */}
        <HeroSection />

        {/* 3. BOOK A COURIER SECTION */}
        <BookingSection preselectedCategory={preselectedCategory} />

        {/* 4. HOW IT WORKS */}
        <HowItWorksSection />

        {/* 5. SERVICES */}
        <ServicesSection
          onSelectCategoryForBooking={(category) =>
            setPreselectedCategory(category)
          }
        />

        {/* 6. SHIPMENT TRACKING */}
        <ShipmentTrackingSection />

        {/* 7. WHY CHOOSE US */}
        <WhyChooseUsSection />
      </main>

      {/* 8. FOOTER */}
      <Footer />

      {/* Customer Login / Supabase Auth Readiness Modal */}
      <AuthReadyModal
        isOpen={loginModalOpen}
        onClose={() => setLoginModalOpen(false)}
      />
    </div>
  );
}
