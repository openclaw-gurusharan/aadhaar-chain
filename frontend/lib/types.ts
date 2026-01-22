// ===== API Request/Response Types =====

// Common Types
export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string | ApiError;
}

// ===== Identity Types =====
export interface Identity {
  did: string;
  owner: string;
  commitment: string;
  verification_bitmap: number;
  credentials_verified: string[];
  created_at: number;
  updated_at: number;
}

export interface CreateIdentityRequest {
  commitment: string;
}

export interface UpdateIdentityRequest {
  commitment?: string;
}

export interface IdentityResponse {
  did: string;
  owner: string;
  commitment: string;
  verification_bitmap: number;
  credentials_verified: string[];
  created_at: number;
  updated_at: number;
}

// ===== Verification Types =====
export interface VerificationStep {
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  message?: string;
  started_at?: number;
  completed_at?: number;
}

export interface VerificationStatus {
  verification_id: string;
  wallet_address: string;
  credential_type: string;
  overall_status: 'pending' | 'processing' | 'verified' | 'failed';
  progress: number;
  steps: VerificationStep[];
  error?: string;
  created_at: number;
  updated_at: number;
}

export interface OverallVerificationStatus {
  wallet_address: string;
  total_verifications: number;
  verified_count: number;
  verifications: Array<{
    credential_type: string;
    status: string;
    progress: number;
  }>;
}

// ===== Credential Types =====
export interface CredentialResponse {
  credential_id: string;
  credential_type: string;
  status: 'active' | 'revoked';
  issued_at: number;
  expires_at?: number;
  claims_summary: Record<string, unknown>;
  revocation_reason?: string;
}

// Credential Data for API Setu fetch
export interface AadhaarData {
  aadhaar_number: string;
}

export interface PanData {
  pan_number: string;
}

export interface DrivingLicenseData {
  dl_number: string;
  dob: string;
}

export interface LandRecordsData {
  state: string;
  district: string;
  survey_number: string;
}

export interface EducationData {
  roll_number: string;
  year: string;
  board?: string;
}

export interface CredentialData {
  credential_type: 'aadhaar' | 'pan' | 'dl' | 'land' | 'education';
  data: AadhaarData | PanData | DrivingLicenseData | LandRecordsData | EducationData;
  fetched_at: number;
}

export interface CredentialRequest {
  credential_type: string;
  data: Record<string, unknown>;
}

// ===== Transaction Types =====
export interface UnsignedTransaction {
  transaction: string;
  blockhash: string;
  last_valid_block_height: number;
}

export interface SignedTransaction {
  transaction: string;
}

export interface TransactionReceipt {
  signature: string;
  slot: number;
  confirmations: number;
  status: 'success' | 'failed';
  error?: string;
}

// ===== Access Grant Types =====
export interface AccessGrant {
  grant_id: string;
  credential_id: string;
  granted_to: string;
  fields: string[];
  purpose: string;
  expires_at: number;
  created_at: number;
  revoked_at?: number;
}

export interface CreateGrantRequest {
  credential_id: string;
  granted_to: string;
  fields?: string[];
  purpose?: string;
  duration_hours?: number;
}

// ===== Wallet Types =====
export interface WalletBalance {
  lamports: number;
  sol: number;
}

// ===== UI State Types =====
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ApiCallState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  retry: () => void;
}

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
  duration?: number;
}

// ===== SSO / Auth Types =====

export interface SessionInfo {
  session_id: number;
  created_at: number;
  last_active: number;
  expires_at: number;
  user_agent?: string;
  ip_address?: string;
}

export interface ConnectedAppInfo {
  app_name: string;
  display_name: string;
  first_accessed: number;
  last_accessed: number;
}

export interface UserResponse {
  wallet_address: string;
  pda_address?: string;
  owner_pubkey?: string;
  created_at: number;
}

export interface LoginRequest {
  wallet_address: string;
  signature?: string;
  email?: string;
}

export interface LoginResponse {
  user: UserResponse;
  session: SessionInfo;
}

export interface ValidateResponse {
  valid: boolean;
  user?: UserResponse;
}

export interface ConnectedAppsResponse {
  apps: ConnectedAppInfo[];
}

export interface SessionsResponse {
  sessions: SessionInfo[];
}
