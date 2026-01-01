import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  Identity,
  CreateIdentityRequest,
  CreateIdentityResponse,
  AadhaarVerificationData,
  PanVerificationData,
  VerificationResponse,
  VerificationStatus,
  Credential,
  CredentialRequest,
  TransactionResponse,
  ApiResponse,
} from './types';

// API base URL from env or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add wallet signature or JWT token here when available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<never>>) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Error setting up request
      console.error('Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ===== IDENTITY MODULE =====
export const identityApi = {
  // Get identity by wallet address
  async getIdentity(walletAddress: string): Promise<Identity> {
    const { data } = await apiClient.get<ApiResponse<Identity>>(
      `/api/identity/${walletAddress}`
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to fetch identity');
    return data.data;
  },

  // Create new identity
  async createIdentity(
    walletAddress: string,
    request: CreateIdentityRequest
  ): Promise<CreateIdentityResponse> {
    const { data } = await apiClient.post<ApiResponse<CreateIdentityResponse>>(
      `/api/identity/${walletAddress}`,
      request
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to create identity');
    return data.data;
  },

  // Update identity commitment
  async updateCommitment(
    walletAddress: string,
    commitment: string
  ): Promise<{ signature: string }> {
    const { data } = await apiClient.patch<ApiResponse<{ signature: string }>>(
      `/api/identity/${walletAddress}`,
      { commitment }
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to update commitment');
    return data.data;
  },
};

// ===== VERIFICATION MODULE =====
export const verificationApi = {
  // Submit Aadhaar verification
  async submitAadhaar(
    walletAddress: string,
    verificationData: AadhaarVerificationData
  ): Promise<VerificationResponse> {
    const { data } = await apiClient.post<ApiResponse<VerificationResponse>>(
      `/api/verification/${walletAddress}/aadhaar`,
      verificationData
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to submit verification');
    return data.data;
  },

  // Submit PAN verification
  async submitPan(
    walletAddress: string,
    verificationData: PanVerificationData
  ): Promise<VerificationResponse> {
    const { data } = await apiClient.post<ApiResponse<VerificationResponse>>(
      `/api/verification/${walletAddress}/pan`,
      verificationData
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to submit verification');
    return data.data;
  },

  // Get verification status
  async getStatus(verificationId: string): Promise<VerificationStatus> {
    const { data } = await apiClient.get<ApiResponse<VerificationStatus>>(
      `/api/verification/status/${verificationId}`
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to fetch status');
    return data.data;
  },
};

// ===== CREDENTIALS MODULE =====
export const credentialsApi = {
  // Get all credentials for wallet
  async getCredentials(walletAddress: string): Promise<Credential[]> {
    const { data } = await apiClient.get<ApiResponse<Credential[]>>(
      `/api/credentials/${walletAddress}`
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to fetch credentials');
    return data.data;
  },

  // Issue new credential
  async issueCredential(
    walletAddress: string,
    request: CredentialRequest
  ): Promise<Credential> {
    const { data } = await apiClient.post<ApiResponse<Credential>>(
      `/api/credentials/${walletAddress}`,
      request
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to issue credential');
    return data.data;
  },

  // Revoke credential
  async revokeCredential(
    walletAddress: string,
    credentialId: string
  ): Promise<{ revoked: boolean }> {
    const { data } = await apiClient.delete<ApiResponse<{ revoked: boolean }>>(
      `/api/credentials/${walletAddress}/${credentialId}`
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to revoke credential');
    return data.data;
  },
};

// ===== TRANSACTION MODULE =====
export const transactionApi = {
  // Prepare unsigned transaction
  async prepareTransaction(
    walletAddress: string,
    instruction: string,
    params: Record<string, unknown>
  ): Promise<{ transaction: string }> {
    const { data } = await apiClient.post<ApiResponse<{ transaction: string }>>(
      `/api/transaction/prepare`,
      { walletAddress, instruction, params }
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to prepare transaction');
    return data.data;
  },

  // Submit signed transaction
  async submitTransaction(signedTransaction: string): Promise<TransactionResponse> {
    const { data } = await apiClient.post<ApiResponse<TransactionResponse>>(
      '/api/transaction/submit',
      { transaction: signedTransaction }
    );
    if (!data.data) throw new Error(data.error?.message || 'Failed to submit transaction');
    return data.data;
  },
};

// Export the api client for direct use if needed
export default apiClient;

// Helper to check if wallet address is valid
export function isValidPublicKey(address: string): boolean {
  try {
    // Base58 check for Solana addresses (typically 32-44 chars)
    return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
  } catch {
    return false;
  }
}
