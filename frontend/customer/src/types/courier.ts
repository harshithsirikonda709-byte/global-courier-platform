export type ParcelCategory =
  | 'clothes_personal'
  | 'homemade_food'
  | 'gifts_family'
  | 'documents';

export interface ParcelCategoryOption {
  id: ParcelCategory;
  label: string;
  description: string;
  complianceNote: string;
}

export interface DestinationCountryOption {
  code: string;
  name: string;
  region: string;
  estimatedTransitDays: string;
  customsAdvisory: string;
}

export interface CourierBookingFormData {
  // Pickup Details (India)
  pickupName: string;
  pickupPhone: string;
  pickupAddress: string;
  pickupCity: string;
  pickupPostalCode: string;

  // Destination Details (Abroad)
  destinationCountry: string;
  destinationCity: string;
  recipientName: string;
  recipientPhone: string;

  // Parcel Details
  parcelCategory: ParcelCategory | '';
  parcelDescription: string;
  estimatedWeight: string;
  preferredPickupDate: string;
}

export type BookingFormErrors = Partial<Record<keyof CourierBookingFormData, string>>;

/**
 * Payload contract prepared for future FastAPI POST /api/v1/bookings endpoint
 * backed by Supabase PostgreSQL.
 */
export interface BookingCreatePayload {
  pickup_name: string;
  pickup_phone: string;
  pickup_address: string;
  pickup_city: string;
  pickup_postal_code: string;
  destination_country: string;
  destination_city: string;
  recipient_name: string;
  recipient_phone: string;
  parcel_category: ParcelCategory;
  parcel_description: string;
  estimated_weight_kg: number;
  preferred_pickup_date: string;
}

export interface ShipmentTrackingQuery {
  trackingNumber: string;
}

export interface NavItem {
  label: string;
  href: string;
}

export interface HowItWorksStep {
  stepNumber: string;
  title: string;
  description: string;
  detailBadge: string;
}

export interface ServiceItem {
  id: ParcelCategory;
  title: string;
  subtitle: string;
  description: string;
  examples: string[];
  regulationNote: string;
}

export interface WhyChooseUsFeature {
  id: string;
  title: string;
  description: string;
  metric: string;
}

