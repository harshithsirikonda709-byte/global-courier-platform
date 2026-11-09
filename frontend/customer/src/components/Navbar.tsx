'use client';

import React, { useState, useEffect } from 'react';
import {
  Globe,
  Menu,
  X,
  PackageCheck,
  LogIn,
  ArrowRight,
  PhoneCall,
} from 'lucide-react';
import { NAV_ITEMS } from '@/data/courierData';

interface NavbarProps {
  onOpenLoginModal: () => void;
}

export default function Navbar({ onOpenLoginModal }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 16);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-md shadow-[0_4px_24px_-6px_rgba(11,31,58,0.1)] border-b border-slate-200/80'
          : 'bg-white border-b border-slate-100'
      }`}
    >
      {/* Top Utility Ribbon */}
      <div className="bg-[#0B1F3A] text-slate-200 text-xs py-2 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-300 font-medium text-[11px] border border-orange-400/30">
              <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
              Doorstep Pickup Across India
            </span>
            <span className="hidden md:inline text-slate-300">
              Sending clothes, homemade food &amp; family parcels to 40+ countries
            </span>
          </div>
          <div className="flex items-center gap-4 text-slate-300">
            <span className="inline-flex items-center gap-1.5">
              <PhoneCall className="w-3.5 h-3.5 text-orange-400" />
              <span>India Support: +91 (800) 120-4500</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <nav
        aria-label="Primary Navigation"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between"
      >
        {/* Brand Logo: GLOBAL COURIER */}
        <a
          href="#home"
          className="flex items-center gap-3 group focus:outline-none"
        >
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-[#0B1F3A] text-white shadow-md shadow-[#0B1F3A]/15 group-hover:bg-[#132d52] transition-colors">
            <Globe className="w-6 h-6 text-orange-400 transition-transform duration-300 group-hover:rotate-12" />
            <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-orange-500 flex items-center justify-center ring-2 ring-white">
              <PackageCheck className="w-2.5 h-2.5 text-white" />
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-lg sm:text-xl font-extrabold tracking-tight text-[#0B1F3A] leading-none">
              GLOBAL <span className="text-orange-600">COURIER</span>
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500 mt-1">
              India to World Logistics
            </span>
          </div>
        </a>

        {/* Desktop Nav Links */}
        <div className="hidden lg:flex items-center gap-1 xl:gap-2">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="px-3.5 py-2 rounded-lg text-sm font-semibold text-slate-700 hover:text-[#0B1F3A] hover:bg-slate-100/80 transition-colors"
            >
              {item.label}
            </a>
          ))}
        </div>

        {/* Desktop Action Buttons */}
        <div className="hidden lg:flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenLoginModal}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-[#0B1F3A] hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer"
          >
            <LogIn className="w-4 h-4 text-slate-600" />
            Login
          </button>
          <a
            href="#book-courier"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-[#0B1F3A] hover:bg-[#142f54] shadow-md shadow-[#0B1F3A]/15 hover:shadow-lg transition-all group"
          >
            <span>Get Started</span>
            <ArrowRight className="w-4 h-4 text-orange-400 transition-transform group-hover:translate-x-0.5" />
          </a>
        </div>

        {/* Mobile Menu Button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
            className="inline-flex items-center justify-center p-2.5 rounded-xl text-[#0B1F3A] hover:bg-slate-100 border border-slate-200 focus:outline-none"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-6 space-y-3 shadow-xl">
          <div className="flex flex-col space-y-1">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={handleNavClick}
                className="px-4 py-3 rounded-xl text-base font-semibold text-slate-800 hover:bg-slate-100 hover:text-[#0B1F3A] transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenLoginModal();
              }}
              className="flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-[#0B1F3A] border border-slate-200 hover:bg-slate-50"
            >
              <LogIn className="w-4 h-4" />
              Login
            </button>
            <a
              href="#book-courier"
              onClick={handleNavClick}
              className="flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-white bg-[#0B1F3A] hover:bg-[#142f54] shadow-sm"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4 text-orange-400" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
}

