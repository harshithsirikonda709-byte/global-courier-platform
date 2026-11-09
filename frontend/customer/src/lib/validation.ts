import {
  BookingCreatePayload,
  BookingFormErrors,
  CourierBookingFormData,
  ParcelCategory,
} from '@/types/courier';

const INDIAN_PHONE_REGEX = /^(?:\+91[\-\s]?)?[6-9]\d{9}$/;
const INTERNATIONAL_PHONE_REGEX = /^\+?[1-9]\d{6,14}$/;
const INDIAN_PINCODE_REGEX = /^[1-9][0-9]{5}$/;
const TRACKING_NUMBER_REGEX = /^(?:GCP[\-\s]?)?[A-Z0-9\-]{6,20}$/i;

export function validateBookingForm(
  data: CourierBookingFormData
): BookingFormErrors {
  const errors: BookingFormErrors = {};

  // 1. Pickup Name
  const pickupName = data.pickupName.trim();
  if (!pickupName) {
    errors.pickupName = 'Pickup contact name is required.';
  } else if (pickupName.length < 2) {
    errors.pickupName = 'Pickup name must be at least 2 characters.';
  } else if (pickupName.length > 80) {
    errors.pickupName = 'Pickup name cannot exceed 80 characters.';
  }

  // 2. Pickup Phone (India)
  const cleanPickupPhone = data.pickupPhone.replace(/\s+/g, '');
  if (!cleanPickupPhone) {
    errors.pickupPhone = 'Indian pickup phone number is required.';
  } else if (!INDIAN_PHONE_REGEX.test(cleanPickupPhone)) {
    errors.pickupPhone =
      'Enter a valid 10-digit Indian mobile number (e.g., +91 9876543210 or 9876543210).';
  }

  // 3. Pickup Address
  const pickupAddress = data.pickupAddress.trim();
  if (!pickupAddress) {
    errors.pickupAddress = 'Complete doorstep pickup address is required.';
  } else if (pickupAddress.length < 10) {
    errors.pickupAddress =
      'Please include house/flat number, street, and landmark (min 10 characters).';
  }

  // 4. Pickup City
  const pickupCity = data.pickupCity.trim();
  if (!pickupCity) {
    errors.pickupCity = 'Pickup city in India is required.';
  } else if (pickupCity.length < 2) {
    errors.pickupCity = 'Enter a valid city name.';
  }

  // 5. Pickup Postal Code (Indian PIN Code)
  const pickupPostalCode = data.pickupPostalCode.trim();
  if (!pickupPostalCode) {
    errors.pickupPostalCode = '6-digit Indian PIN code is required.';
  } else if (!INDIAN_PINCODE_REGEX.test(pickupPostalCode)) {
    errors.pickupPostalCode = 'Enter a valid 6-digit Indian PIN code (e.g., 400001).';
  }

  // 6. Destination Country
  if (!data.destinationCountry.trim()) {
    errors.destinationCountry = 'Please select a destination country.';
  }

  // 7. Destination City
  const destinationCity = data.destinationCity.trim();
  if (!destinationCity) {
    errors.destinationCity = 'Destination city abroad is required.';
  } else if (destinationCity.length < 2) {
    errors.destinationCity = 'Enter a valid destination city.';
  }

  // 8. Recipient Name
  const recipientName = data.recipientName.trim();
  if (!recipientName) {
    errors.recipientName = 'Recipient full name is required.';
  } else if (recipientName.length < 2) {
    errors.recipientName = 'Recipient name must be at least 2 characters.';
  }

  // 9. Recipient Phone
  const cleanRecipientPhone = data.recipientPhone.replace(/[\s\-()]+/g, '');
  if (!cleanRecipientPhone) {
    errors.recipientPhone = 'Recipient international phone number is required.';
  } else if (!INTERNATIONAL_PHONE_REGEX.test(cleanRecipientPhone)) {
    errors.recipientPhone =
      'Enter a valid international number with country code (e.g., +1 4155550198).';
  }

  // 10. Parcel Category
  if (!data.parcelCategory) {
    errors.parcelCategory = 'Please select a parcel category.';
  }

  // 11. Parcel Description
  const parcelDescription = data.parcelDescription.trim();
  if (!parcelDescription) {
    errors.parcelDescription = 'Itemized parcel description is required for customs.';
  } else if (parcelDescription.length < 10) {
    errors.parcelDescription =
      'Please list the contents clearly for customs screening (at least 10 characters).';
  } else if (parcelDescription.length > 500) {
    errors.parcelDescription = 'Description cannot exceed 500 characters.';
  }

  // 12. Estimated Weight
  const weightRaw = data.estimatedWeight.trim();
  if (!weightRaw) {
    errors.estimatedWeight = 'Estimated parcel weight (in kg) is required.';
  } else {
    const weightNum = Number(weightRaw);
    if (Number.isNaN(weightNum) || weightNum <= 0) {
      errors.estimatedWeight = 'Enter a valid positive weight in kg.';
    } else if (weightNum < 0.5) {
      errors.estimatedWeight = 'Minimum billable weight is 0.5 kg.';
    } else if (weightNum > 70) {
      errors.estimatedWeight =
        'Single parcel weight cannot exceed 70 kg. Contact support for cargo freight.';
    }
  }

  // 13. Preferred Pickup Date
  if (!data.preferredPickupDate) {
    errors.preferredPickupDate = 'Please select a preferred pickup date.';
  } else {
    const selectedDate = new Date(`${data.preferredPickupDate}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (Number.isNaN(selectedDate.getTime())) {
      errors.preferredPickupDate = 'Invalid date format.';
    } else if (selectedDate < today) {
      errors.preferredPickupDate = 'Pickup date cannot be in the past.';
    }
  }

  return errors;
}

export function validateTrackingNumber(trackingNumber: string): string | null {
  const trimmed = trackingNumber.trim();
  if (!trimmed) {
    return 'Please enter a shipment tracking number.';
  }
  if (!TRACKING_NUMBER_REGEX.test(trimmed)) {
    return 'Enter a valid 6–20 character alphanumeric tracking reference (e.g., GCP-2026-84920).';
  }
  return null;
}

/**
 * Maps validated customer form state to the snake_case FastAPI schema payload
 * prepared for future POST /api/v1/bookings integration.
 */
export function toFastApiBookingPayload(
  data: CourierBookingFormData
): BookingCreatePayload {
  return {
    pickup_name: data.pickupName.trim(),
    pickup_phone: data.pickupPhone.trim(),
    pickup_address: data.pickupAddress.trim(),
    pickup_city: data.pickupCity.trim(),
    pickup_postal_code: data.pickupPostalCode.trim(),
    destination_country: data.destinationCountry.trim(),
    destination_city: data.destinationCity.trim(),
    recipient_name: data.recipientName.trim(),
    recipient_phone: data.recipientPhone.trim(),
    parcel_category: data.parcelCategory as ParcelCategory,
    parcel_description: data.parcelDescription.trim(),
    estimated_weight_kg: Number(data.estimatedWeight),
    preferred_pickup_date: data.preferredPickupDate,
  };
}

