'use client';

import { useEffect, useCallback, useRef } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { useCredentialStore } from '@/stores/credentials';
import { CredentialInputForm } from './CredentialInputForm';
import { OTPVerification } from './OTPVerification';
import { DataPreview } from './DataPreview';
import { getCredentialConfig } from '@/lib/credentials';

interface FetchCredentialModalProps {
  open: boolean;
  onClose: () => void;
  onComplete?: () => void;
}

export function FetchCredentialModal({ open, onClose, onComplete }: FetchCredentialModalProps) {
  const { connected, publicKey } = useWallet();
  const handleCompleteCalledRef = useRef(false);
  const {
    activeType,
    step,
    fetchedData,
    loading,
    error,
    otpAttempts,
    maxOtpAttempts,
    submitForm,
    verifyOTP,
    resendOTP,
    confirmAndStore,
    closeModal,
    reset,
  } = useCredentialStore();

  const config = activeType ? getCredentialConfig(activeType) : null;

  // Handle close
  const handleClose = useCallback(() => {
    closeModal();
    onClose();
  }, [closeModal, onClose]);

  // Handle completion - using ref to avoid multiple calls
  const handleComplete = useCallback(() => {
    if (handleCompleteCalledRef.current) return;
    handleCompleteCalledRef.current = true;

    if (onComplete) {
      onComplete();
    }
    setTimeout(() => {
      handleClose();
      reset();
      handleCompleteCalledRef.current = false;
    }, 2000);
  }, [onComplete, handleClose, reset]);

  // Form submission handler
  const handleFormSubmit = async (data: Record<string, string>) => {
    if (!publicKey) {
      return;
    }
    await submitForm(publicKey.toString(), data);
  };

  // OTP verification handler
  const handleOTPVerify = async (otpValue: string) => {
    if (!publicKey) {
      return;
    }
    await verifyOTP(publicKey.toString(), otpValue);
  };

  // OTP resend handler
  const handleResendOTP = async () => {
    if (!publicKey) {
      return;
    }
    await resendOTP(publicKey.toString());
  };

  // Confirm and store handler
  const handleConfirmStore = async () => {
    if (!publicKey) {
      return;
    }
    await confirmAndStore(publicKey.toString());
    if (step === 'success') {
      handleComplete();
    }
  };

  // Edit handler (go back to input step)
  const handleEdit = () => {
    useCredentialStore.getState().setStep('input');
  };

  // Auto-close on success after delay
  useEffect(() => {
    if (step === 'success') {
      const timer = setTimeout(handleComplete, 1500);
      return () => clearTimeout(timer);
    }
  }, [step, handleComplete]);

  if (!config) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl">{config.title}</DialogTitle>
          <DialogDescription>
            {config.description}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Input Step */}
        {step === 'input' && (
          <>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Enter the required details to fetch your {config.title.toLowerCase()}
              </p>
              <CredentialInputForm
                type={activeType!}
                onSubmit={handleFormSubmit}
                loading={loading}
                disabled={!connected}
              />
            </div>
          </>
        )}

        {/* OTP Step */}
        {step === 'otp' && (
          <OTPVerification
            onSubmit={handleOTPVerify}
            onCancel={handleClose}
            onResend={handleResendOTP}
            loading={loading}
            disabled={!connected}
            maxAttempts={maxOtpAttempts}
            attemptsRemaining={maxOtpAttempts - otpAttempts}
          />
        )}

        {/* Preview Step */}
        {step === 'preview' && fetchedData && (
          <DataPreview
            data={fetchedData}
            credentialType={activeType!}
            onConfirm={handleConfirmStore}
            onEdit={handleEdit}
            loading={loading}
            disabled={!connected}
          />
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <div className="py-12 text-center space-y-6">
            <Loader2 className="h-12 w-12 animate-spin text-muted-foreground mx-auto" />
            <p className="text-lg font-semibold">Storing Credential</p>
            <p className="text-sm text-muted-foreground">
              Saving to blockchain...
            </p>
          </div>
        )}

        {/* Success Step */}
        {step === 'success' && (
          <div className="py-12 text-center space-y-6">
            <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle2 className="h-8 w-8 text-green-700" />
            </div>
            <p className="text-xl font-semibold">
              Credential Verified!
            </p>
            <p className="text-sm text-muted-foreground max-w-sm mx-auto">
              Your {config.title.toLowerCase()} has been successfully stored on the blockchain
            </p>
            <Button onClick={handleClose} className="mt-4">
              Close
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
