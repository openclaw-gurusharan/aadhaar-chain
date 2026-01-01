'use client';

import { useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, Loader2, Upload } from 'lucide-react';

type VerificationStep = 'upload' | 'consent' | 'otp' | 'processing' | 'complete' | 'error';

export default function VerifyAadhaarPage() {
  const { connected } = useWallet();
  const [step, setStep] = useState<VerificationStep>('upload');
  const [aadhaarNumber, setAadhaarNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmitDocument = async () => {
    if (!aadhaarNumber.match(/^\d{12}$/)) {
      setError('Please enter a valid 12-digit Aadhaar number');
      return;
    }
    if (!consent) {
      setError('Please accept the consent agreement');
      return;
    }
    setStep('otp');
  };

  const handleVerifyOtp = async () => {
    if (!otp.match(/^\d{6}$/)) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setStep('processing');
    setError('');
    setProgress(0);

    // Simulate verification process
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 500);

    setTimeout(() => {
      clearInterval(interval);
      setProgress(100);
      setStep('complete');
    }, 5000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Aadhaar Verification</h1>
        <p className="text-muted-foreground">
          Verify your identity using Aadhaar
        </p>
      </div>

      {!connected && (
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to continue
          </AlertDescription>
        </Alert>
      )}

      {/* Upload Step */}
      {step === 'upload' && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Upload your Aadhaar card (PDF or image)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".pdf,image/*"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-sm text-muted-foreground">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </p>
              </label>
            </div>

            <div className="space-y-2">
              <Label htmlFor="aadhaar">Aadhaar Number</Label>
              <Input
                id="aadhaar"
                placeholder="12-digit Aadhaar number"
                value={aadhaarNumber}
                onChange={(e) => setAadhaarNumber(e.target.value.replace(/\D/g, '').slice(0, 12))}
                maxLength={12}
              />
            </div>

            {error && (
              <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
                <AlertDescription className="text-red-800 dark:text-red-200">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <Button onClick={handleSubmitDocument} disabled={!connected || !file}>
              Continue
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Consent Step */}
      {step === 'consent' && (
        <Card>
          <CardHeader>
            <CardTitle>Consent Agreement</CardTitle>
            <CardDescription>
              Please review and accept the consent terms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted p-4 rounded-lg text-sm space-y-2 max-h-60 overflow-y-auto">
              <p><strong>Purpose of Verification:</strong></p>
              <p>I hereby consent to the use of my Aadhaar details for identity verification on the blockchain platform.</p>
              <p><strong>Data Usage:</strong></p>
              <p>My information will be used solely for verification purposes and stored as a hash commitment on-chain.</p>
              <p><strong>Rights:</strong></p>
              <p>I understand I have the right to revoke this consent at any time.</p>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm">I accept the consent terms</span>
            </label>

            <Button onClick={() => setStep('otp')} disabled={!consent}>
              Send OTP
            </Button>
          </CardContent>
        </Card>
      )}

      {/* OTP Step */}
      {step === 'otp' && (
        <Card>
          <CardHeader>
            <CardTitle>Enter OTP</CardTitle>
            <CardDescription>
              Enter the 6-digit OTP sent to your Aadhaar-linked mobile
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="otp">OTP</Label>
              <Input
                id="otp"
                placeholder="6-digit OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                className="text-center text-2xl tracking-widest"
              />
            </div>

            {error && (
              <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
                <AlertDescription className="text-red-800 dark:text-red-200">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <Button onClick={handleVerifyOtp} disabled={otp.length !== 6}>
              Verify OTP
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Processing Step */}
      {step === 'processing' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              Processing Verification
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-muted-foreground text-center">
              {progress < 30 ? 'Validating document...' :
               progress < 60 ? 'Checking for tampering...' :
               progress < 90 ? 'Cross-referencing databases...' :
               'Finalizing verification...'}
            </p>
            <div className="space-y-2 text-sm">
              <div className={progress >= 20 ? 'text-green-600' : 'text-muted-foreground'}>
                {progress >= 20 ? '✓' : '○'} Document parsing
              </div>
              <div className={progress >= 40 ? 'text-green-600' : 'text-muted-foreground'}>
                {progress >= 40 ? '✓' : '○'} Fraud detection check
              </div>
              <div className={progress >= 60 ? 'text-green-600' : 'text-muted-foreground'}>
                {progress >= 60 ? '✓' : '○'} Compliance verification
              </div>
              <div className={progress >= 80 ? 'text-green-600' : 'text-muted-foreground'}>
                {progress >= 80 ? '✓' : '○'} Blockchain update
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Complete Step */}
      {step === 'complete' && (
        <Card className="border-green-200 bg-green-50 dark:bg-green-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
              <CheckCircle2 className="h-6 w-6" />
              Verification Successful
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-green-700 dark:text-green-300">
              Your Aadhaar has been successfully verified. Your identity has been updated on-chain.
            </p>
            <Button asChild>
              <a href="/dashboard">Return to Dashboard</a>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
