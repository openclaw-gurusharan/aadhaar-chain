/**
 * Credential type definitions and configuration
 * Maps to API Setu credential types
 */
'use client';

import { FileText, CreditCard, Car, Home, GraduationCap, LucideIcon } from 'lucide-react';

export type CredentialType = 'aadhaar' | 'pan' | 'dl' | 'land' | 'education';

export type FetchStep = 'input' | 'otp' | 'preview' | 'processing' | 'success';

export interface CredentialField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select';
  placeholder?: string;
  pattern?: RegExp;
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  min?: number;
  max?: number;
}

export interface CredentialConfig {
  id: CredentialType;
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
  fields: CredentialField[];
}

/**
 * Indian states for Land Records dropdown
 */
export const INDIAN_STATES = [
  { value: 'maharashtra', label: 'Maharashtra' },
  { value: 'karnataka', label: 'Karnataka' },
  { value: 'tamil-nadu', label: 'Tamil Nadu' },
  { value: 'telangana', label: 'Telangana' },
  { value: 'andhra-pradesh', label: 'Andhra Pradesh' },
  { value: 'kerala', label: 'Kerala' },
  { value: 'gujarat', label: 'Gujarat' },
  { value: 'rajasthan', label: 'Rajasthan' },
  { value: 'uttar-pradesh', label: 'Uttar Pradesh' },
  { value: 'delhi', label: 'Delhi' },
  { value: 'west-bengal', label: 'West Bengal' },
  { value: 'madhya-pradesh', label: 'Madhya Pradesh' },
];

/**
 * Credential type configurations
 */
export const CREDENTIAL_TYPES: Record<CredentialType, CredentialConfig> = {
  aadhaar: {
    id: 'aadhaar',
    title: 'Aadhaar Card',
    description: 'Unique Identification Authority of India',
    icon: FileText,
    color: 'orange',
    fields: [
      {
        name: 'aadhaar_number',
        label: 'Aadhaar Number',
        type: 'text',
        placeholder: '12-digit Aadhaar number',
        pattern: /^\d{12}$/,
        required: true,
      },
    ],
  },
  pan: {
    id: 'pan',
    title: 'PAN Card',
    description: 'Permanent Account Number - Income Tax Department',
    icon: CreditCard,
    color: 'blue',
    fields: [
      {
        name: 'pan_number',
        label: 'PAN Number',
        type: 'text',
        placeholder: 'ABCDE1234F',
        pattern: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
        required: true,
      },
    ],
  },
  dl: {
    id: 'dl',
    title: 'Driving License',
    description: 'Transport Department - Government of India',
    icon: Car,
    color: 'purple',
    fields: [
      {
        name: 'dl_number',
        label: 'DL Number',
        type: 'text',
        placeholder: 'Your driving license number',
        required: true,
      },
      {
        name: 'dob',
        label: 'Date of Birth',
        type: 'date',
        required: true,
      },
    ],
  },
  land: {
    id: 'land',
    title: 'Land Records',
    description: 'Property Ownership Documents',
    icon: Home,
    color: 'green',
    fields: [
      {
        name: 'state',
        label: 'State',
        type: 'select',
        options: INDIAN_STATES,
        required: true,
      },
      {
        name: 'district',
        label: 'District',
        type: 'text',
        placeholder: 'Enter district name',
        required: true,
      },
      {
        name: 'survey_number',
        label: 'Survey Number',
        type: 'text',
        placeholder: 'Property survey number',
        required: true,
      },
    ],
  },
  education: {
    id: 'education',
    title: 'Education Certificate',
    description: 'Academic Qualifications & Marksheets',
    icon: GraduationCap,
    color: 'indigo',
    fields: [
      {
        name: 'roll_number',
        label: 'Roll Number',
        type: 'text',
        placeholder: 'Your roll number',
        required: true,
      },
      {
        name: 'year',
        label: 'Year of Passing',
        type: 'number',
        min: 1990,
        max: new Date().getFullYear(),
        required: true,
      },
      {
        name: 'board',
        label: 'Board/University (Optional)',
        type: 'text',
        placeholder: 'CBSE, ICSE, State Board, etc.',
        required: false,
      },
    ],
  },
};

/**
 * Preview field mappings for each credential type
 * These fields are displayed in the preview step after OTP verification
 */
export const PREVIEW_FIELDS: Record<CredentialType, string[]> = {
  aadhaar: ['name', 'dob', 'gender', 'address', 'pincode'],
  pan: ['pan_number', 'name', 'father_name', 'dob', 'pan_status'],
  dl: ['dl_number', 'name', 'dob', 'address', 'issue_date', 'expiry_date', 'vehicle_classes'],
  land: ['property_id', 'owner_name', 'property_address', 'area', 'ownership_type'],
  education: ['degree', 'university', 'year', 'student_name', 'specialization'],
};

/**
 * Field labels for preview display
 */
export const FIELD_LABELS: Record<string, string> = {
  // Aadhaar
  name: 'Full Name',
  dob: 'Date of Birth',
  gender: 'Gender',
  address: 'Address',
  pincode: 'PIN Code',

  // PAN
  pan_number: 'PAN Number',
  father_name: "Father's Name",
  pan_status: 'PAN Status',

  // Driving License
  dl_number: 'DL Number',
  issue_date: 'Issue Date',
  expiry_date: 'Expiry Date',
  vehicle_classes: 'Vehicle Classes',

  // Land Records
  property_id: 'Property ID',
  owner_name: 'Owner Name',
  property_address: 'Property Address',
  area: 'Area',
  ownership_type: 'Ownership Type',

  // Education
  degree: 'Degree',
  university: 'University/Board',
  year: 'Year',
  student_name: 'Student Name',
  specialization: 'Specialization',
};

/**
 * Get credential config by type
 */
export function getCredentialConfig(type: CredentialType): CredentialConfig {
  return CREDENTIAL_TYPES[type];
}

/**
 * Get all credential types as array
 */
export function getAllCredentialTypes(): CredentialType[] {
  return Object.keys(CREDENTIAL_TYPES) as CredentialType[];
}

/**
 * Validate form data for a credential type
 */
export function validateCredentialData(
  type: CredentialType,
  data: Record<string, string>
): { valid: boolean; errors: Record<string, string> } {
  const config = getCredentialConfig(type);
  const errors: Record<string, string> = {};

  for (const field of config.fields) {
    const value = data[field.name];

    // Check required fields
    if (field.required && !value) {
      errors[field.name] = `${field.label} is required`;
      continue;
    }

    // Skip validation for empty optional fields
    if (!value && !field.required) {
      continue;
    }

    // Pattern validation
    if (field.pattern && value && !field.pattern.test(value)) {
      errors[field.name] = `Invalid ${field.label.toLowerCase()} format`;
    }

    // Number range validation
    if (field.type === 'number' && value) {
      const numValue = parseInt(value, 10);
      if (field.min !== undefined && numValue < field.min) {
        errors[field.name] = `${field.label} must be at least ${field.min}`;
      }
      if (field.max !== undefined && numValue > field.max) {
        errors[field.name] = `${field.label} must be at most ${field.max}`;
      }
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}
