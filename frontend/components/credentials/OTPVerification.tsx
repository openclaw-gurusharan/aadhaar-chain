'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

interface OTPVerificationProps {
  onSubmit: (otp: string) => Promise<void>;
  onCancel: () => void;
  onResend?: () => Promise<void>;
  loading?: boolean;
  disabled?: boolean;
  maxAttempts?: number;
  attemptsRemaining?: number;
}

export function OTPVerification({
  onSubmit,
  onCancel,
  onResend,
  loading = false,
  disabled = false,
  maxAttempts = 3,
  attemptsRemaining = maxAttempts,
}: OTPVerificationProps) {
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [resendCountdown, setResendCountdown] = useState(30);

  // Countdown timer for resend button
  useEffect(() => {
    if (resendCountdown > 0) {
      const timer = setTimeout(() => setResendCountdown(resendCountdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCountdown]);

  const canResend = resendCountdown === 0;

  const handleResend = async () => {
    if (onResend && canResend) {
      try {
        await onResend();
        setResendCountdown(30);
        setOtp('');
        setError('');
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Failed to resend OTP';
        setError(message);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setError('');
    try {
      await onSubmit(otp);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'OTP verification failed';
      setError(message);
    }
  };

  const handleOtpChange = (value: string) => {
    // Only allow digits
    const numericValue = value.replace(/\D/g, '');
    setOtp(numericValue.slice(0, 6));
    if (error) setError('');
  };

  return (
    <div className="space-y-4">
      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">
          Enter the 6-digit OTP sent to your Aadhaar-linked mobile number
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Input
            type="text"
            inputMode="numeric"
            maxLength={6}
            placeholder="Enter 6-digit OTP"
            value={otp}
            onChange={(e) => handleOtpChange(e.target.value)}
            disabled={disabled || loading}
            className="text-center text-2xl tracking-widest"
            autoFocus
          />
        </div>

        {attemptsRemaining < maxAttempts && attemptsRemaining > 0 && (
          <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
            <AlertDescription className="text-yellow-800 dark:text-yellow-200">
              {attemptsRemaining} {attemptsRemaining === 1 ? 'attempt' : 'attempts'} remaining
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={disabled || loading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={disabled || loading || otp.length !== 6}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify OTP'
            )}
          </Button>
        </div>

        {onResend && (
          <div className="text-center">
            <Button
              type="button"
              variant="link"
              size="sm"
              onClick={handleResend}
              disabled={!canResend || disabled || loading}
              className="text-sm"
            >
              {canResend ? 'Resend OTP' : `Resend OTP in ${resendCountdown}s`}
            </Button>
          </div>
        )}
      </form>
    </div>
  );
}
