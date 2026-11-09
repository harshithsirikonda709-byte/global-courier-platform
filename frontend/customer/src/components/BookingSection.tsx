'use client';

import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Globe2,
  Package,
  Calendar,
  Scale,
  User,
  Phone,
  FileText,
  AlertCircle,
  Info,
  Send,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  CheckCircle,
} from 'lucide-react';
import {
  BookingCreatePayload,
  BookingFormErrors,
  CourierBookingFormData,
  ParcelCategory,
} from '@/types/courier';
import {
  DESTINATION_COUNTRIES,
  PARCEL_CATEGORIES,
  POPULAR_INDIAN_CITIES,
} from '@/data/courierData';
import {
  toFastApiBookingPayload,
  validateBookingForm,
} from '@/lib/validation';
import { FASTAPI_ENDPOINTS } from '@/lib/apiConfig';

interface BookingSectionProps {
  preselectedCategory?: ParcelCategory | '';
}

const INITIAL_FORM_STATE: CourierBookingFormData = {
  pickupName: '',
  pickupPhone: '',
  pickupAddress: '',
  pickupCity: '',
  pickupPostalCode: '',
  destinationCountry: '',
  destinationCity: '',
  recipientName: '',
  recipientPhone: '',
  parcelCategory: '',
  parcelDescription: '',
  estimatedWeight: '',
  preferredPickupDate: '',
};

export default function BookingSection({
  preselectedCategory,
}: BookingSectionProps) {
  const [formData, setFormData] =
    useState<CourierBookingFormData>(INITIAL_FORM_STATE);
  const [errors, setErrors] = useState<BookingFormErrors>({});
  const [validatedPayload, setValidatedPayload] =
    useState<BookingCreatePayload | null>(null);
  const [minDate, setMinDate] = useState<string>('');

  useEffect(() => {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    setMinDate(`${yyyy}-${mm}-${dd}`);
  }, []);

  useEffect(() => {
    if (preselectedCategory) {
      setFormData((prev) => ({
        ...prev,
        parcelCategory: preselectedCategory,
      }));
      setErrors((prev) => ({ ...prev, parcelCategory: undefined }));
    }
  }, [preselectedCategory]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    const fieldName = name as keyof CourierBookingFormData;

    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));

    if (errors[fieldName]) {
      setErrors((prev) => ({
        ...prev,
        [fieldName]: undefined,
      }));
    }

    if (validatedPayload) {
      setValidatedPayload(null);
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const validationErrors = validateBookingForm(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      setValidatedPayload(null);
      return;
    }

    // Transform validated form values into the FastAPI schema payload.
    // Per implementation rules: No dummy API call is made, and we do NOT claim
    // that the booking is confirmed without backend integration.
    const payload = toFastApiBookingPayload(formData);
    setValidatedPayload(payload);
  };

  const handleReset = () => {
    setFormData(INITIAL_FORM_STATE);
    setErrors({});
    setValidatedPayload(null);
  };

  const selectedCountryInfo = DESTINATION_COUNTRIES.find(
    (c) => c.name === formData.destinationCountry
  );

  const selectedCategoryInfo = PARCEL_CATEGORIES.find(
    (cat) => cat.id === formData.parcelCategory
  );

  const errorCount = Object.values(errors).filter(Boolean).length;

  return (
    <section
      id="book-courier"
      className="py-20 lg:py-28 bg-slate-50 border-b border-slate-200/80 scroll-mt-20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-14">
          <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-50 border border-orange-200 text-orange-700 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            Doorstep International Booking
          </span>
          <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold text-[#0B1F3A] tracking-tight">
            Book a Doorstep Courier Pickup
          </h2>
          <p className="mt-3 text-base sm:text-lg text-slate-600">
            Fill in your Indian pickup address, overseas recipient details, and
            parcel information. Our team verifies customs eligibility and packs
            your shipment at pickup.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-start">
          {/* Left 8 Columns: Complete Booking Form */}
          <div className="lg:col-span-8">
            <form
              onSubmit={handleSubmit}
              noValidate
              className="bg-white rounded-3xl shadow-xl shadow-slate-900/5 border border-slate-200/90 overflow-hidden"
            >
              {/* Form Top Banner */}
              <div className="bg-[#0B1F3A] px-6 sm:px-8 py-5 text-white flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold">
                    Shipment Pickup &amp; Customs Declaration Form
                  </h3>
                  <p className="text-xs text-slate-300 mt-0.5">
                    All fields are required for international airway bill
                    preparation
                  </p>
                </div>
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-white/10 text-orange-300 border border-white/15">
                  India → Worldwide
                </span>
              </div>

              <div className="p-6 sm:p-8 space-y-10">
                {/* Validation Error Summary Alert */}
                {errorCount > 0 && (
                  <div
                    role="alert"
                    className="rounded-2xl bg-red-50 border border-red-200 p-4 flex items-start gap-3 text-red-900"
                  >
                    <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-bold">
                        Please correct {errorCount}{' '}
                        {errorCount === 1 ? 'field' : 'fields'} before
                        submitting:
                      </p>
                      <p className="text-xs text-red-700 mt-0.5">
                        Check the highlighted inputs below for required format
                        details.
                      </p>
                    </div>
                  </div>
                )}

                {/* STEP GROUP 1: PICKUP DETAILS (INDIA) */}
                <div>
                  <div className="flex items-center gap-2.5 pb-4 mb-6 border-b border-slate-200">
                    <div className="w-8 h-8 rounded-lg bg-[#0B1F3A] text-white flex items-center justify-center font-bold text-sm">
                      1
                    </div>
                    <div>
                      <h4 className="text-base font-extrabold text-[#0B1F3A]">
                        Pickup Details (India)
                      </h4>
                      <p className="text-xs text-slate-500">
                        Where should our pickup executive visit to collect the
                        parcel?
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {/* Pickup Name */}
                    <div>
                      <label
                        htmlFor="pickupName"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Pickup Name <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="pickupName"
                          name="pickupName"
                          type="text"
                          value={formData.pickupName}
                          onChange={handleChange}
                          placeholder="e.g., Rajesh Sharma"
                          aria-invalid={Boolean(errors.pickupName)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.pickupName
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.pickupName && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.pickupName}
                        </p>
                      )}
                    </div>

                    {/* Pickup Phone */}
                    <div>
                      <label
                        htmlFor="pickupPhone"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Pickup Phone (India){' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="pickupPhone"
                          name="pickupPhone"
                          type="tel"
                          value={formData.pickupPhone}
                          onChange={handleChange}
                          placeholder="e.g., +91 9876543210"
                          aria-invalid={Boolean(errors.pickupPhone)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.pickupPhone
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.pickupPhone && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.pickupPhone}
                        </p>
                      )}
                    </div>

                    {/* Pickup Address */}
                    <div className="sm:col-span-2">
                      <label
                        htmlFor="pickupAddress"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Pickup Address{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
                        <input
                          id="pickupAddress"
                          name="pickupAddress"
                          type="text"
                          value={formData.pickupAddress}
                          onChange={handleChange}
                          placeholder="Flat / House No., Building, Street, Area & Landmark"
                          aria-invalid={Boolean(errors.pickupAddress)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.pickupAddress
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.pickupAddress && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.pickupAddress}
                        </p>
                      )}
                    </div>

                    {/* Pickup City */}
                    <div>
                      <label
                        htmlFor="pickupCity"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Pickup City <span className="text-orange-600">*</span>
                      </label>
                      <input
                        id="pickupCity"
                        name="pickupCity"
                        type="text"
                        list="indian-cities-list"
                        value={formData.pickupCity}
                        onChange={handleChange}
                        placeholder="e.g., Mumbai, Ahmedabad, Bengaluru"
                        aria-invalid={Boolean(errors.pickupCity)}
                        className={`w-full px-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                          errors.pickupCity
                            ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                            : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                        }`}
                      />
                      <datalist id="indian-cities-list">
                        {POPULAR_INDIAN_CITIES.map((city) => (
                          <option key={city} value={city} />
                        ))}
                      </datalist>
                      {errors.pickupCity && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.pickupCity}
                        </p>
                      )}
                    </div>

                    {/* Pickup Postal Code */}
                    <div>
                      <label
                        htmlFor="pickupPostalCode"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Pickup Postal Code (PIN){' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <input
                        id="pickupPostalCode"
                        name="pickupPostalCode"
                        type="text"
                        inputMode="numeric"
                        maxLength={6}
                        value={formData.pickupPostalCode}
                        onChange={handleChange}
                        placeholder="6-digit PIN Code (e.g., 400001)"
                        aria-invalid={Boolean(errors.pickupPostalCode)}
                        className={`w-full px-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                          errors.pickupPostalCode
                            ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                            : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                        }`}
                      />
                      {errors.pickupPostalCode && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.pickupPostalCode}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* STEP GROUP 2: DESTINATION & RECIPIENT DETAILS (ABROAD) */}
                <div>
                  <div className="flex items-center gap-2.5 pb-4 mb-6 border-b border-slate-200">
                    <div className="w-8 h-8 rounded-lg bg-[#0B1F3A] text-white flex items-center justify-center font-bold text-sm">
                      2
                    </div>
                    <div>
                      <h4 className="text-base font-extrabold text-[#0B1F3A]">
                        Destination &amp; Recipient Details (Abroad)
                      </h4>
                      <p className="text-xs text-slate-500">
                        Who is receiving the parcel overseas?
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {/* Destination Country */}
                    <div>
                      <label
                        htmlFor="destinationCountry"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Destination Country{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Globe2 className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <select
                          id="destinationCountry"
                          name="destinationCountry"
                          value={formData.destinationCountry}
                          onChange={handleChange}
                          aria-invalid={Boolean(errors.destinationCountry)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 focus:outline-none focus:ring-2 transition-all ${
                            errors.destinationCountry
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        >
                          <option value="">Select destination country</option>
                          {DESTINATION_COUNTRIES.map((country) => (
                            <option key={country.code} value={country.name}>
                              {country.name} ({country.estimatedTransitDays})
                            </option>
                          ))}
                        </select>
                      </div>
                      {errors.destinationCountry && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.destinationCountry}
                        </p>
                      )}
                    </div>

                    {/* Destination City */}
                    <div>
                      <label
                        htmlFor="destinationCity"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Destination City{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <input
                        id="destinationCity"
                        name="destinationCity"
                        type="text"
                        value={formData.destinationCity}
                        onChange={handleChange}
                        placeholder="e.g., New Jersey, London, Toronto, Sydney"
                        aria-invalid={Boolean(errors.destinationCity)}
                        className={`w-full px-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                          errors.destinationCity
                            ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                            : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                        }`}
                      />
                      {errors.destinationCity && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.destinationCity}
                        </p>
                      )}
                    </div>

                    {/* Recipient Name */}
                    <div>
                      <label
                        htmlFor="recipientName"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Recipient Name{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="recipientName"
                          name="recipientName"
                          type="text"
                          value={formData.recipientName}
                          onChange={handleChange}
                          placeholder="Full name as on recipient ID"
                          aria-invalid={Boolean(errors.recipientName)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.recipientName
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.recipientName && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.recipientName}
                        </p>
                      )}
                    </div>

                    {/* Recipient Phone */}
                    <div>
                      <label
                        htmlFor="recipientPhone"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Recipient Phone (With Country Code){' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="recipientPhone"
                          name="recipientPhone"
                          type="tel"
                          value={formData.recipientPhone}
                          onChange={handleChange}
                          placeholder="e.g., +1 4155550198 or +44 7700900077"
                          aria-invalid={Boolean(errors.recipientPhone)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.recipientPhone
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.recipientPhone && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.recipientPhone}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* STEP GROUP 3: PARCEL SPECIFICATION & SCHEDULE */}
                <div>
                  <div className="flex items-center gap-2.5 pb-4 mb-6 border-b border-slate-200">
                    <div className="w-8 h-8 rounded-lg bg-[#0B1F3A] text-white flex items-center justify-center font-bold text-sm">
                      3
                    </div>
                    <div>
                      <h4 className="text-base font-extrabold text-[#0B1F3A]">
                        Parcel Contents, Weight &amp; Pickup Date
                      </h4>
                      <p className="text-xs text-slate-500">
                        Specify what you are sending so our team brings the
                        right packing material
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {/* Parcel Category */}
                    <div className="sm:col-span-2">
                      <label
                        htmlFor="parcelCategory"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Parcel Category{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Package className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <select
                          id="parcelCategory"
                          name="parcelCategory"
                          value={formData.parcelCategory}
                          onChange={handleChange}
                          aria-invalid={Boolean(errors.parcelCategory)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 focus:outline-none focus:ring-2 transition-all ${
                            errors.parcelCategory
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        >
                          <option value="">Select parcel category</option>
                          {PARCEL_CATEGORIES.map((category) => (
                            <option key={category.id} value={category.id}>
                              {category.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      {errors.parcelCategory && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.parcelCategory}
                        </p>
                      )}
                    </div>

                    {/* Parcel Description */}
                    <div className="sm:col-span-2">
                      <label
                        htmlFor="parcelDescription"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Parcel Description{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <FileText className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
                        <textarea
                          id="parcelDescription"
                          name="parcelDescription"
                          rows={3}
                          value={formData.parcelDescription}
                          onChange={handleChange}
                          placeholder="List items clearly (e.g., 4 cotton kurtas, 2 kg dry homemade besan laddoo, 1 kg roasted namkeen)"
                          aria-invalid={Boolean(errors.parcelDescription)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.parcelDescription
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      <div className="mt-1 flex items-center justify-between">
                        {errors.parcelDescription ? (
                          <p className="text-xs font-medium text-red-600">
                            {errors.parcelDescription}
                          </p>
                        ) : (
                          <p className="text-xs text-slate-500">
                            Accurate itemization helps ensure smooth customs
                            clearance.
                          </p>
                        )}
                        <span className="text-xs text-slate-400">
                          {formData.parcelDescription.length}/500
                        </span>
                      </div>
                    </div>

                    {/* Estimated Weight */}
                    <div>
                      <label
                        htmlFor="estimatedWeight"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Estimated Weight (kg){' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Scale className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="estimatedWeight"
                          name="estimatedWeight"
                          type="number"
                          step="0.5"
                          min="0.5"
                          max="70"
                          value={formData.estimatedWeight}
                          onChange={handleChange}
                          placeholder="e.g., 5.0"
                          aria-invalid={Boolean(errors.estimatedWeight)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-all ${
                            errors.estimatedWeight
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.estimatedWeight && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.estimatedWeight}
                        </p>
                      )}
                    </div>

                    {/* Preferred Pickup Date */}
                    <div>
                      <label
                        htmlFor="preferredPickupDate"
                        className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2"
                      >
                        Preferred Pickup Date{' '}
                        <span className="text-orange-600">*</span>
                      </label>
                      <div className="relative">
                        <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        <input
                          id="preferredPickupDate"
                          name="preferredPickupDate"
                          type="date"
                          min={minDate}
                          value={formData.preferredPickupDate}
                          onChange={handleChange}
                          aria-invalid={Boolean(errors.preferredPickupDate)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm text-slate-900 focus:outline-none focus:ring-2 transition-all ${
                            errors.preferredPickupDate
                              ? 'border-red-400 bg-red-50/40 focus:ring-red-200'
                              : 'border-slate-300 bg-white focus:border-[#0B1F3A] focus:ring-[#0B1F3A]/15'
                          }`}
                        />
                      </div>
                      {errors.preferredPickupDate && (
                        <p className="mt-1.5 text-xs font-medium text-red-600">
                          {errors.preferredPickupDate}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                  <button
                    type="button"
                    onClick={handleReset}
                    className="inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl text-sm font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors cursor-pointer"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Clear Form
                  </button>

                  <button
                    type="submit"
                    className="inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl text-base font-bold text-white bg-orange-600 hover:bg-orange-500 shadow-lg shadow-orange-600/20 hover:shadow-xl transition-all cursor-pointer"
                  >
                    <Send className="w-4 h-4" />
                    <span>Submit Booking</span>
                  </button>
                </div>

                {/* Transparent Validation Result (No Fake Confirmation!) */}
                {validatedPayload && (
                  <div
                    role="status"
                    aria-live="polite"
                    className="mt-6 rounded-2xl bg-[#0B1F3A] text-white p-6 border border-orange-400/40 shadow-lg space-y-4"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-400/40 flex items-center justify-center shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-orange-400" />
                        </div>
                        <div>
                          <span className="inline-block text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-400/30 mb-1.5">
                            Frontend Validation Passed • Backend Not Yet Connected
                          </span>
                          <h4 className="text-base sm:text-lg font-bold text-white">
                            Booking Details Validated (Not Yet Confirmed)
                          </h4>
                          <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
                            Your pickup request from{' '}
                            <strong className="text-white">
                              {validatedPayload.pickup_city} (
                              {validatedPayload.pickup_postal_code})
                            </strong>{' '}
                            to{' '}
                            <strong className="text-white">
                              {validatedPayload.destination_city},{' '}
                              {validatedPayload.destination_country}
                            </strong>{' '}
                            has passed client-side validation.{' '}
                            <span className="text-orange-300 font-semibold">
                              This booking is not confirmed yet
                            </span>{' '}
                            because the FastAPI (
                            <code className="text-xs bg-white/10 px-1.5 py-0.5 rounded">
                              POST {FASTAPI_ENDPOINTS.bookings}
                            </code>
                            ) and Supabase database endpoints are pending
                            integration.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Prepared FastAPI Payload Preview */}
                    <div className="rounded-xl bg-slate-950/80 border border-white/10 p-4">
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                        <span className="font-mono font-semibold text-orange-300">
                          Prepared FastAPI Payload Contract
                        </span>
                        <span>Ready for Supabase Persistence</span>
                      </div>
                      <pre className="text-xs font-mono text-slate-200 overflow-x-auto leading-relaxed">
                        {JSON.stringify(validatedPayload, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </form>
          </div>

          {/* Right 4 Columns: Live Advisory & Booking Guidance Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            {/* Dynamic Destination Country Advisory Card */}
            <div className="bg-white rounded-3xl p-6 shadow-lg shadow-slate-900/5 border border-slate-200/90">
              <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
                <div className="w-10 h-10 rounded-xl bg-[#0B1F3A] text-orange-400 flex items-center justify-center shrink-0">
                  <Globe2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-extrabold text-[#0B1F3A] uppercase tracking-wider">
                    Destination Customs Guide
                  </h3>
                  <p className="text-xs text-slate-500">
                    Real-time corridor compliance notes
                  </p>
                </div>
              </div>

              {selectedCountryInfo ? (
                <div className="mt-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-base font-extrabold text-[#0B1F3A]">
                      {selectedCountryInfo.name}
                    </span>
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-orange-50 text-orange-700 border border-orange-200">
                      {selectedCountryInfo.estimatedTransitDays}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                    {selectedCountryInfo.customsAdvisory}
                  </p>
                </div>
              ) : (
                <p className="mt-4 text-xs text-slate-500 leading-relaxed">
                  Select a{' '}
                  <strong className="text-slate-700">
                    Destination Country
                  </strong>{' '}
                  in the form to view estimated express transit times and
                  country-specific customs regulations.
                </p>
              )}
            </div>

            {/* Dynamic Parcel Category Packing Note */}
            <div className="bg-white rounded-3xl p-6 shadow-lg shadow-slate-900/5 border border-slate-200/90">
              <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
                <div className="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 border border-orange-200 flex items-center justify-center shrink-0">
                  <Info className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-extrabold text-[#0B1F3A] uppercase tracking-wider">
                    Category Packing Standard
                  </h3>
                  <p className="text-xs text-slate-500">
                    Doorstep verification checklist
                  </p>
                </div>
              </div>

              {selectedCategoryInfo ? (
                <div className="mt-4 space-y-2.5">
                  <p className="text-sm font-bold text-[#0B1F3A]">
                    {selectedCategoryInfo.label}
                  </p>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {selectedCategoryInfo.description}
                  </p>
                  <div className="p-3 rounded-xl bg-amber-50/90 border border-amber-200/80 text-xs text-amber-900">
                    <strong className="font-bold">Compliance Note: </strong>
                    {selectedCategoryInfo.complianceNote}
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-xs text-slate-500 leading-relaxed">
                  Choose a{' '}
                  <strong className="text-slate-700">Parcel Category</strong> to
                  see how our pickup team seals and prepares your items for
                  export.
                </p>
              )}
            </div>

            {/* Prohibited Items Quick Notice */}
            <div className="rounded-3xl bg-[#0B1F3A] text-white p-6 space-y-3">
              <div className="flex items-center gap-2.5 text-orange-400">
                <ShieldAlert className="w-5 h-5 shrink-0" />
                <h4 className="text-sm font-bold uppercase tracking-wider">
                  Important Customs Notice
                </h4>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                All parcels undergo open-box verification during doorstep pickup
                in India. Pressurized aerosols, lithium batteries, currency,
                gold/silver bullion, alcohol, and unsealed liquids cannot be
                shipped via international air cargo.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

