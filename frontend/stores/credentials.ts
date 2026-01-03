import { create } from 'zustand';
import { CredentialType, FetchStep } from '@/lib/credentials';
import { credentialsApi } from '@/lib/api';

interface CredentialState {
  // Modal state
  modalOpen: boolean;
  activeType: CredentialType | null;
  step: FetchStep;

  // Form data
  formData: Record<string, string>;
  otp: string;

  // Fetched data
  fetchedData: Record<string, unknown> | null;

  // Loading and error states
  loading: boolean;
  error: string | null;

  // OTP attempts tracking
  otpAttempts: number;
  maxOtpAttempts: number;

  // Actions
  openModal: (type: CredentialType) => void;
  closeModal: () => void;
  setStep: (step: FetchStep) => void;

  // Form actions
  setFormData: (data: Record<string, string>) => void;
  submitForm: (walletAddress: string, data: Record<string, string>) => Promise<void>;

  // OTP actions
  setOtp: (otp: string) => void;
  verifyOTP: (walletAddress: string, otp: string) => Promise<void>;
  resendOTP: (walletAddress: string) => Promise<void>;

  // Confirm actions
  confirmAndStore: (walletAddress: string) => Promise<void>;

  // Reset
  reset: () => void;
}

const initialState = {
  modalOpen: false,
  activeType: null,
  step: 'input' as FetchStep,
  formData: {},
  otp: '',
  fetchedData: null,
  loading: false,
  error: null,
  otpAttempts: 0,
  maxOtpAttempts: 3,
};

export const useCredentialStore = create<CredentialState>((set, get) => ({
  ...initialState,

  openModal: (type: CredentialType) => {
    set({
      modalOpen: true,
      activeType: type,
      step: 'input',
      formData: {},
      otp: '',
      fetchedData: null,
      error: null,
      otpAttempts: 0,
      loading: false,
    });
  },

  closeModal: () => {
    set({
      modalOpen: false,
      activeType: null,
      step: 'input',
      formData: {},
      otp: '',
      fetchedData: null,
      error: null,
      otpAttempts: 0,
      loading: false,
    });
  },

  setStep: (step: FetchStep) => {
    set({ step });
  },

  setFormData: (data: Record<string, string>) => {
    set({ formData: data });
  },

  submitForm: async (walletAddress: string, data: Record<string, string>) => {
    const { activeType } = get();

    if (!activeType) {
      set({ error: 'No credential type selected' });
      return;
    }

    set({ loading: true, error: null, formData: data });

    try {
      // Step 1: Send OTP by calling API Setu
      const response = await credentialsApi.fetchAndTokenize(walletAddress, {
        credential_type: activeType,
        data,
      });

      // OTP sent successfully
      set({
        step: 'otp',
        loading: false,
      });
    } catch (error: unknown) {
      const message = error instanceof Error && 'response' in error
        ? ((error as any).response?.data?.message || error.message)
        : 'Failed to send OTP';
      set({
        error: message,
        loading: false,
      });
    }
  },

  setOtp: (otp: string) => {
    set({ otp });
  },

  verifyOTP: async (walletAddress: string, otp: string) => {
    const { activeType, formData } = get();

    if (!activeType) {
      set({ error: 'No credential type selected' });
      return;
    }

    set({ loading: true, error: null, otp });

    try {
      // Step 2: Verify OTP and fetch credential data
      const response = await credentialsApi.fetchAndTokenize(walletAddress, {
        credential_type: activeType,
        data: {
          ...formData,
          otp,
        },
      });

      // OTP verified successfully, show preview
      set({
        step: 'preview',
        fetchedData: (response as unknown as { data?: Record<string, unknown> }).data || response.claims_summary,
        loading: false,
      });
    } catch (error: unknown) {
      const attempts = get().otpAttempts + 1;
      const message = error instanceof Error && 'response' in error
        ? ((error as any).response?.data?.message || error.message)
        : 'OTP verification failed';
      set({
        error: message,
        loading: false,
        otpAttempts: attempts,
      });

      // Check if max attempts reached
      if (attempts >= get().maxOtpAttempts) {
        set({
          error: 'Maximum OTP attempts exceeded. Please try again.',
          step: 'input',
          otpAttempts: 0,
        });
      }
    }
  },

  resendOTP: async (walletAddress: string) => {
    const { activeType, formData } = get();

    if (!activeType) {
      set({ error: 'No credential type selected' });
      return;
    }

    set({ loading: true, error: null });

    try {
      await credentialsApi.fetchAndTokenize(walletAddress, {
        credential_type: activeType,
        data: formData,
      });

      set({
        loading: false,
        otp: '',
        otpAttempts: 0,
      });
    } catch (error: unknown) {
      const message = error instanceof Error && 'response' in error
        ? ((error as any).response?.data?.message || error.message)
        : 'Failed to resend OTP';
      set({
        error: message,
        loading: false,
      });
    }
  },

  confirmAndStore: async (walletAddress: string) => {
    const { activeType, formData, otp } = get();

    if (!activeType) {
      set({ error: 'No credential type selected' });
      return;
    }

    set({ loading: true, error: null, step: 'processing' });

    try {
      // Step 3: Confirm and store credential
      const response = await credentialsApi.fetchAndTokenize(walletAddress, {
        credential_type: activeType,
        data: {
          ...formData,
          otp,
          confirm: true,
        },
      });

      set({
        step: 'success',
        loading: false,
      });
    } catch (error: unknown) {
      const message = error instanceof Error && 'response' in error
        ? ((error as any).response?.data?.message || error.message)
        : 'Failed to store credential';
      set({
        error: message,
        loading: false,
        step: 'preview',
      });
    }
  },

  reset: () => {
    set(initialState);
  },
}));
