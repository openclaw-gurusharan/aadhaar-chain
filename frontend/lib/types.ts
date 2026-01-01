// API Request/Response Types

export interface PublicKey {
  toBase58(): string;
}

// Identity Types
export interface Identity {
  did: string;
  owner: string;
  commitment: string;
  verificationBitmap: number;
  createdAt: number;
  updatedAt: number;
}

export interface CreateIdentityRequest {
  commitment: string;
}

export interface CreateIdentityResponse {
  identity: Identity;
  signature: string;
}

// Verification Types
export interface VerificationRequest {
  documentType: 'aadhaar' | 'pan';
  documentData: string | File;
}

export interface AadhaarVerificationData {
  aadhaarNumber: string;
  otp: string;
  documentHash?: string;
}

export interface PanVerificationData {
  panNumber: string;
  fullName: string;
  dateOfBirth: string;
  documentHash?: string;
}

export interface VerificationResponse {
  success: boolean;
  verificationId: string;
  status: 'pending' | 'processing' | 'verified' | 'failed';
  message: string;
}

export interface VerificationStatus {
  verificationId: string;
  status: 'pending' | 'processing' | 'verified' | 'failed';
  progress: number;
  steps: {
    name: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
  }[];
  error?: string;
}

// Credential Types
export interface Credential {
  id: string;
  type: string;
  issuer: string;
  subject: string;
  issuanceDate: number;
  expirationDate: number;
  revoked: boolean;
  claims: Record<string, unknown>;
}

export interface CredentialRequest {
  type: string;
  claims: Record<string, unknown>;
}

// Wallet Types
export interface WalletBalance {
  lamports: number;
  sol: number;
}

export interface TransactionResponse {
  signature: string;
  success: boolean;
  error?: string;
}

// API Error Types
export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
}
