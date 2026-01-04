import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { toast } from '@/stores/toast';
import type {
  IdentityResponse,
  CredentialResponse,
  VerificationStatus,
  OverallVerificationStatus,
  AccessGrant,
  CreateIdentityRequest,
  UpdateIdentityRequest,
  CredentialRequest,
  CreateGrantRequest,
  UnsignedTransaction,
  TransactionReceipt,
  ApiResponse,
} from './types';

// API base URL from env or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;
const RETRYABLE_STATUS = [500, 502, 503, 504];

// Sleep helper for retry delay
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store for wallet signature callback
let walletSignCallback: ((message: string) => Promise<string>) | null = null;

/**
 * Set the wallet signing callback for authentication
 * This should be called when wallet is connected
 */
export function setWalletSignCallback(callback: (message: string) => Promise<string>) {
  walletSignCallback = callback;
}

/**
 * Clear the wallet signing callback
 */
export function clearWalletSignCallback() {
  walletSignCallback = null;
}

// Request interceptor - add wallet signature auth
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Add wallet signature for authentication if available
    if (walletSignCallback && config.headers) {
      try {
        // Create timestamp for nonce
        const timestamp = Date.now();
        const message = `Sign this message to authenticate with Identity Platform\nTimestamp: ${timestamp}`;

        const signature = await walletSignCallback(message);
        config.headers['X-Wallet-Address'] = signature; // This should be wallet address
        config.headers['X-Wallet-Signature'] = signature;
        config.headers['X-Timestamp'] = timestamp.toString();
      } catch (error) {
        console.error('Failed to sign request:', error);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors with retry logic
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiResponse<never>>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: number };

    if (!originalRequest) {
      return Promise.reject(error);
    }

    // Initialize retry counter
    if (originalRequest._retry === undefined) {
      originalRequest._retry = 0;
    }

    const status = error.response?.status;

    // Check if error is retryable
    if (
      status &&
      RETRYABLE_STATUS.includes(status) &&
      originalRequest._retry < MAX_RETRIES
    ) {
      originalRequest._retry += 1;
      const delay = RETRY_DELAY_MS * Math.pow(2, originalRequest._retry - 1); // Exponential backoff

      console.warn(`Retrying request (attempt ${originalRequest._retry}/${MAX_RETRIES}) after ${delay}ms`);

      await sleep(delay);
      return apiClient(originalRequest);
    }

    // Handle error responses
    if (error.response) {
      const data = error.response.data as ApiResponse<never>;
      const errorMessage = typeof data.error === 'string' ? data.error : data.error?.message || error.message;

      // Show toast for user-facing errors
      if (status !== 401 && status !== 403) {
        toast.error(errorMessage);
      }

      console.error('API Error:', { status, errorMessage });
    } else if (error.request) {
      // Request made but no response
      const errorMessage = 'Network error. Please check your connection.';
      toast.error(errorMessage);
      console.error('Network Error:', error.message);
    } else {
      // Error setting up request
      toast.error(error.message || 'An error occurred');
      console.error('Request Error:', error.message);
    }

    return Promise.reject(error);
  }
);

// ===== IDENTITY MODULE =====
export const identityApi = {
  /**
   * Get identity by wallet address
   */
  async getIdentity(walletAddress: string): Promise<IdentityResponse> {
    const { data } = await apiClient.get<ApiResponse<IdentityResponse>>(
      `/api/identity/${walletAddress}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch identity');
    }

    return data.data;
  },

  /**
   * Create new identity
   */
  async createIdentity(
    walletAddress: string,
    request: CreateIdentityRequest
  ): Promise<UnsignedTransaction> {
    const { data } = await apiClient.post<ApiResponse<UnsignedTransaction>>(
      `/api/identity/${walletAddress}`,
      request
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to create identity');
    }

    return data.data;
  },

  /**
   * Update identity commitment
   */
  async updateCommitment(
    walletAddress: string,
    request: UpdateIdentityRequest
  ): Promise<UnsignedTransaction> {
    const { data } = await apiClient.patch<ApiResponse<UnsignedTransaction>>(
      `/api/identity/${walletAddress}`,
      request
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to update identity');
    }

    return data.data;
  },
};

// ===== CREDENTIALS MODULE =====
export const credentialsApi = {
  /**
   * Get all credentials for wallet
   */
  async getCredentials(walletAddress: string): Promise<CredentialResponse[]> {
    const { data } = await apiClient.get<ApiResponse<CredentialResponse[]>>(
      `/api/credentials/${walletAddress}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch credentials');
    }

    return data.data;
  },

  /**
   * Step 1: Initiate credential fetch (send OTP)
   */
  async initiate(
    walletAddress: string,
    credentialType: string,
    formData: Record<string, string>
  ): Promise<{ session_id: string; otp?: string; mock_mode: boolean }> {
    const { data } = await apiClient.post<ApiResponse<{ session_id: string; otp?: string; mock_mode: boolean }>>(
      `/api/credentials/${walletAddress}/initiate`,
      { credential_type: credentialType, data: formData }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to initiate credential fetch');
    }

    return data.data;
  },

  /**
   * Step 2: Verify OTP and get preview data
   */
  async verify(
    walletAddress: string,
    credentialType: string,
    formData: Record<string, string>,
    otp: string
  ): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post<ApiResponse<{ credential_data: Record<string, unknown> }>>(
      `/api/credentials/${walletAddress}/verify`,
      { credential_type: credentialType, data: formData, otp }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'OTP verification failed');
    }

    return data.data.credential_data;
  },

  /**
   * Step 3: Confirm and store credential
   */
  async confirm(
    walletAddress: string,
    credentialType: string,
    formData: Record<string, string>,
    otp: string
  ): Promise<CredentialResponse> {
    const { data } = await apiClient.post<ApiResponse<CredentialResponse>>(
      `/api/credentials/${walletAddress}/confirm`,
      { credential_type: credentialType, data: formData, otp }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to store credential');
    }

    toast.success('Credential stored successfully');
    return data.data;
  },

  /**
   * Legacy: Fetch from API Setu and tokenize credential (single-step)
   * Use initiate -> verify -> confirm instead
   */
  async fetchAndTokenize(
    walletAddress: string,
    request: CredentialRequest
  ): Promise<CredentialResponse> {
    const { data } = await apiClient.post<ApiResponse<CredentialResponse>>(
      `/api/credentials/${walletAddress}`,
      request
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch credential');
    }

    return data.data;
  },

  /**
   * Get specific credential by type
   */
  async getCredential(walletAddress: string, credentialType: string): Promise<CredentialResponse> {
    const { data } = await apiClient.get<ApiResponse<CredentialResponse>>(
      `/api/credentials/${walletAddress}/${credentialType}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch credential');
    }

    return data.data;
  },

  /**
   * Revoke credential
   */
  async revokeCredential(
    walletAddress: string,
    credentialId: string
  ): Promise<{ message: string }> {
    const { data } = await apiClient.delete<ApiResponse<{ message: string }>>(
      `/api/credentials/${walletAddress}/${credentialId}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to revoke credential');
    }

    toast.success('Credential revoked successfully');
    return data.data;
  },
};

// ===== VERIFICATION MODULE =====
export const verificationApi = {
  /**
   * Get overall verification status for wallet
   */
  async getOverallStatus(walletAddress: string): Promise<OverallVerificationStatus> {
    const { data } = await apiClient.get<ApiResponse<OverallVerificationStatus>>(
      `/api/verification/${walletAddress}/status`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch verification status');
    }

    return data.data;
  },

  /**
   * Get specific verification status
   */
  async getVerificationStatus(verificationId: string): Promise<VerificationStatus> {
    const { data } = await apiClient.get<ApiResponse<VerificationStatus>>(
      `/api/verification/${verificationId}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch verification status');
    }

    return data.data;
  },

  /**
   * Start verification process
   */
  async startVerification(
    walletAddress: string,
    credentialType: string
  ): Promise<VerificationStatus> {
    const { data } = await apiClient.post<ApiResponse<VerificationStatus>>(
      `/api/verification/${walletAddress}/${credentialType}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to start verification');
    }

    toast.info('Verification started');
    return data.data;
  },

  /**
   * Update verification progress (internal use)
   */
  async updateProgress(
    verificationId: string,
    progress: number,
    stepName?: string,
    stepStatus?: string,
    message?: string
  ): Promise<VerificationStatus> {
    const { data } = await apiClient.patch<ApiResponse<VerificationStatus>>(
      `/api/verification/${verificationId}/progress`,
      { progress, step_name: stepName, step_status: stepStatus, message }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to update progress');
    }

    return data.data;
  },
};

// ===== TRANSACTION MODULE =====
export const transactionApi = {
  /**
   * Prepare unsigned transaction
   */
  async prepareTransaction(
    instructions: unknown[],
    payer: string
  ): Promise<UnsignedTransaction> {
    const { data } = await apiClient.post<ApiResponse<UnsignedTransaction>>(
      '/api/transaction/prepare',
      { instructions, payer }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to prepare transaction');
    }

    return data.data;
  },

  /**
   * Submit signed transaction
   */
  async submitTransaction(signedTransaction: string): Promise<TransactionReceipt> {
    const { data } = await apiClient.post<ApiResponse<TransactionReceipt>>(
      '/api/transaction/submit',
      { transaction: signedTransaction }
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to submit transaction');
    }

    if (data.data.status === 'success') {
      toast.success('Transaction submitted successfully');
    } else {
      toast.error(data.data.error || 'Transaction failed');
    }

    return data.data;
  },
};

// ===== ACCESS GRANTS MODULE =====
export const grantsApi = {
  /**
   * Create access grant
   */
  async createGrant(walletAddress: string, request: CreateGrantRequest): Promise<AccessGrant> {
    const { data } = await apiClient.post<ApiResponse<AccessGrant>>(
      `/api/grant/${walletAddress}`,
      request
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to create grant');
    }

    toast.success('Access granted successfully');
    return data.data;
  },

  /**
   * List active grants for wallet
   */
  async listGrants(walletAddress: string): Promise<AccessGrant[]> {
    const { data } = await apiClient.get<ApiResponse<AccessGrant[]>>(
      `/api/grants/${walletAddress}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to fetch grants');
    }

    return data.data;
  },

  /**
   * Revoke access grant
   */
  async revokeGrant(walletAddress: string, grantId: string): Promise<{ message: string }> {
    const { data } = await apiClient.delete<ApiResponse<{ message: string }>>(
      `/api/grants/${walletAddress}/${grantId}`
    );

    if (!data.success || !data.data) {
      throw new Error(typeof data.error === 'string' ? data.error : 'Failed to revoke grant');
    }

    toast.success('Access revoked successfully');
    return data.data;
  },
};

// ===== HEALTH CHECK =====
export const healthApi = {
  async check(): Promise<{ status: string; version: string }> {
    const { data } = await apiClient.get<{ status: string; version: string }>('/api/health');
    return data;
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
