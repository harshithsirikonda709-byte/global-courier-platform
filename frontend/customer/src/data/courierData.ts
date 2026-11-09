import {
  DestinationCountryOption,
  HowItWorksStep,
  NavItem,
  ParcelCategoryOption,
  ServiceItem,
  WhyChooseUsFeature,
} from '@/types/courier';

export const NAV_ITEMS: NavItem[] = [
  { label: 'Home', href: '#home' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Services', href: '#services' },
  { label: 'Track Shipment', href: '#track-shipment' },
];

export const DESTINATION_COUNTRIES: DestinationCountryOption[] = [
  {
    code: 'US',
    name: 'United States',
    region: 'North America',
    estimatedTransitDays: '4–6 Business Days',
    customsAdvisory:
      'FDA prior notice rules apply for homemade food; commercial-grade vacuum sealing handled by our hub.',
  },
  {
    code: 'GB',
    name: 'United Kingdom',
    region: 'Europe',
    estimatedTransitDays: '3–5 Business Days',
    customsAdvisory:
      'Personal gifts and dry snacks permitted; dairy and meat products are strictly restricted by UK customs.',
  },
  {
    code: 'CA',
    name: 'Canada',
    region: 'North America',
    estimatedTransitDays: '4–6 Business Days',
    customsAdvisory:
      'CFIA regulations permit dry packaged snacks, spices, and personal apparel with itemized declaration.',
  },
  {
    code: 'AU',
    name: 'Australia',
    region: 'Oceania',
    estimatedTransitDays: '5–7 Business Days',
    customsAdvisory:
      'Strict biosecurity inspection (DAFF). Seeds, raw nuts, and dairy items are prohibited; clear ingredient labels required.',
  },
  {
    code: 'AE',
    name: 'United Arab Emirates',
    region: 'Middle East',
    estimatedTransitDays: '2–4 Business Days',
    customsAdvisory:
      'Fast-track customs clearance for family parcels, garments, sweets, and dry homemade foods.',
  },
  {
    code: 'DE',
    name: 'Germany',
    region: 'Europe (EU)',
    estimatedTransitDays: '4–6 Business Days',
    customsAdvisory:
      'EU customs rules require full HS code itemization; non-perishable dry goods and personal clothes accepted.',
  },
  {
    code: 'SG',
    name: 'Singapore',
    region: 'Southeast Asia',
    estimatedTransitDays: '3–4 Business Days',
    customsAdvisory:
      'SFA personal food import allowances apply up to 5 kg for permitted dry food products.',
  },
  {
    code: 'NZ',
    name: 'New Zealand',
    region: 'Oceania',
    estimatedTransitDays: '5–8 Business Days',
    customsAdvisory:
      'MPI biosecurity rules require detailed declaration of all food and plant-based ingredients.',
  },
  {
    code: 'IE',
    name: 'Ireland',
    region: 'Europe (EU)',
    estimatedTransitDays: '4–6 Business Days',
    customsAdvisory:
      'Personal garments, books, gifts, and dry shelf-stable snacks accepted subject to EU customs norms.',
  },
];

export const PARCEL_CATEGORIES: ParcelCategoryOption[] = [
  {
    id: 'clothes_personal',
    label: 'Clothes and Personal Belongings',
    description:
      'Traditional Indian wear, seasonal garments, footwear, bedding, utensils, and student essentials.',
    complianceNote:
      'Must be clean and dry. Commercial resale quantities require separate export documentation.',
  },
  {
    id: 'homemade_food',
    label: 'Permitted Homemade Food Products',
    description:
      'Dry snacks, laddoos, chakli, namkeen, roasted spices, pickles (oil-sealed), and festival sweets.',
    complianceNote:
      'Subject to destination biosecurity and customs laws. Perishable, liquid-heavy, or meat/dairy items may be restricted.',
  },
  {
    id: 'gifts_family',
    label: 'Gifts and Family Packages',
    description:
      'Festival hampers (Diwali, Rakhi), handicrafts, non-precious jewelry, books, and children’s items.',
    complianceNote:
      'Batteries, aerosols, perfumes, precious bullion, and currency are strictly prohibited in air cargo.',
  },
  {
    id: 'documents',
    label: 'Documents',
    description:
      'University transcripts, legal certificates, property papers, invitations, and official dossiers.',
    complianceNote:
      'Shipped in tamper-evident waterproof envelopes. Government passports or original currency cannot be shipped.',
  },
];

export const HOW_IT_WORKS_STEPS: HowItWorksStep[] = [
  {
    stepNumber: '01',
    title: 'Book Online',
    description:
      'Enter pickup address in India, destination abroad, and parcel details to schedule a convenient home visit.',
    detailBadge: 'Takes 2 Minutes',
  },
  {
    stepNumber: '02',
    title: 'Driver Visits Your Home',
    description:
      'Our verified executive arrives at your doorstep across major Indian cities and towns at your chosen date.',
    detailBadge: 'Doorstep Collection',
  },
  {
    stepNumber: '03',
    title: 'Parcel Verification & Packing',
    description:
      'Items are inspected for destination customs compliance, weighed digitally, vacuum-sealed, and packed in 5-ply export boxes.',
    detailBadge: 'Export-Grade Packing',
  },
  {
    stepNumber: '04',
    title: 'International Partner Handover',
    description:
      'Consolidated customs paperwork is completed at our hub and handed over to tier-1 global air express networks.',
    detailBadge: 'Customs Cleared',
  },
  {
    stepNumber: '05',
    title: 'Delivery Abroad',
    description:
      'Your parcel travels via priority air freight and is delivered safely to your loved ones’ doorstep overseas.',
    detailBadge: 'Signed Delivery',
  },
];

export const SERVICE_ITEMS: ServiceItem[] = [
  {
    id: 'clothes_personal',
    title: 'Clothes and Personal Belongings',
    subtitle: 'Apparel, Ethnic Wear & Student Essentials',
    description:
      'Send sarees, kurtas, winter jackets, footwear, pressure cookers, and everyday household belongings to students and families settled abroad.',
    examples: [
      'Festive & ethnic Indian wear',
      'Winter coats & thermal wear',
      'Steel kitchenware & utensils',
      'Books & study material',
    ],
    regulationNote:
      'Accepted in all major destinations when declared for personal, non-commercial use.',
  },
  {
    id: 'homemade_food',
    title: 'Permitted Homemade Food Products',
    subtitle: 'Taste of Home, Packed for International Transit',
    description:
      'From Mom’s handmade laddoos and theplas to homemade masalas and pickles—we vacuum-seal and label items to meet international air transit standards.',
    examples: [
      'Dry snacks, namkeen & sweets',
      'Homemade spice blends & powders',
      'Leak-proof vacuum-sealed pickles',
      'Festival farsan & dry fruits',
    ],
    regulationNote:
      'Acceptance strictly depends on destination-country agricultural and food safety regulations (e.g., US FDA, Australia DAFF, UK DEFRA).',
  },
  {
    id: 'gifts_family',
    title: 'Gifts and Family Packages',
    subtitle: 'Curated Care Packages for Every Celebration',
    description:
      'Celebrate Diwali, Raksha Bandhan, birthdays, weddings, and graduations across continents with thoughtfully packed family care boxes.',
    examples: [
      'Rakhi & Diwali celebration hampers',
      'Handicrafts & home decor items',
      'Toys, games & baby clothing',
      'Custom multi-item family care boxes',
    ],
    regulationNote:
      'Gift duty exemptions vary by destination country customs valuation thresholds.',
  },
  {
    id: 'documents',
    title: 'Documents',
    subtitle: 'Priority Express Envelope Service',
    description:
      'Fast, secure international air delivery for critical academic, legal, and personal paperwork in tamper-resistant protective sleeves.',
    examples: [
      'University transcripts & degrees',
      'Attested legal & property documents',
      'Medical records & prescriptions',
      'Wedding invitations & certificates',
    ],
    regulationNote:
      'Passports, bearer cheques, and cash are prohibited by international aviation and Indian postal laws.',
  },
];

export const WHY_CHOOSE_US_FEATURES: WhyChooseUsFeature[] = [
  {
    id: 'doorstep-pickup',
    title: 'Doorstep Pickup Across India',
    description:
      'No need for parents or elders to carry heavy boxes to courier offices. Our verified pickup executives collect directly from home.',
    metric: '500+ Indian PIN Codes',
  },
  {
    id: 'packing-assistance',
    title: 'Professional Packing Assistance',
    description:
      'Multi-layer bubble wrapping, vacuum sealing for food items, and reinforced corrugated export cartons to protect against air transit pressure.',
    metric: 'Vacuum & 5-Ply Export Grade',
  },
  {
    id: 'transparent-pricing',
    title: 'Transparent Weight-Based Pricing',
    description:
      'Clear volumetric and dead-weight calculation explained upfront with zero hidden fuel surcharges or surprise handling fees.',
    metric: 'Upfront Cost Breakdown',
  },
  {
    id: 'shipment-tracking',
    title: 'End-to-End Milestone Tracking',
    description:
      'Monitor every stage from home collection and hub packing in India to customs clearance and final doorstep delivery abroad.',
    metric: 'Real-Time Milestone Updates',
  },
  {
    id: 'logistics-partners',
    title: 'Tier-1 International Logistics Partners',
    description:
      'Integrated handover with leading global express aviation networks ensuring reliable transit schedules to 40+ countries.',
    metric: 'Global Air Express Network',
  },
];

export const POPULAR_INDIAN_CITIES: string[] = [
  'Mumbai',
  'Delhi / NCR',
  'Bengaluru',
  'Hyderabad',
  'Ahmedabad',
  'Chennai',
  'Pune',
  'Kolkata',
  'Surat',
  'Vadodara',
  'Jaipur',
  'Kochi',
  'Chandigarh',
  'Indore',
  'Nagpur',
  'Coimbatore',
];

