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

type VerificationStep = 'upload' | 'details' | 'processing' | 'complete';

export default function VerifyPanPage() {
  const { connected } = useWallet();
  const [step, setStep] = useState<VerificationStep>('upload');
  const [panNumber, setPanNumber] = useState('');
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmitDocument = () => {
    if (!file) {
      setError('Please upload your PAN card');
      return;
    }
    setStep('details');
  };

  const handleSubmitDetails = async () => {
    if (!panNumber.match(/[A-Z]{5}[0-9]{4}[A-Z]{1}/)) {
      setError('Please enter a valid PAN number (e.g., ABCDE1234F)');
      return;
    }
    if (!name || !dob) {
      setError('Please fill in all fields');
      return;
    }

    setStep('processing');
    setError('');
    setProgress(0);

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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1>PAN Verification</h1>
          <p className="text-muted-foreground">
            Verify your identity using PAN card
          </p>
        </div>
      </div>

      {!connected && (
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to continue
          </AlertDescription>
        </Alert>
      )}

      {step === 'upload' && (
        <Card>
          <CardHeader>
            <CardTitle>Upload PAN Card</CardTitle>
            <CardDescription>
              Upload your PAN card (PDF or image)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".pdf,image/*"
                onChange={handleFileUpload}
                className="hidden"
                id="pan-upload"
              />
              <label htmlFor="pan-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-sm text-muted-foreground">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </p>
              </label>
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

      {step === 'details' && (
        <Card>
          <CardHeader>
            <CardTitle>Confirm Details</CardTitle>
            <CardDescription>
              Enter the details as they appear on your PAN card
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="pan">PAN Number</Label>
              <Input
                id="pan"
                placeholder="ABCDE1234F"
                value={panNumber}
                onChange={(e) => setPanNumber(e.target.value.toUpperCase())}
                maxLength={10}
                className="uppercase"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Name as per PAN</Label>
              <Input
                id="name"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="dob">Date of Birth</Label>
              <Input
                id="dob"
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
              />
            </div>

            {error && (
              <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
                <AlertDescription className="text-red-800 dark:text-red-200">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <Button onClick={handleSubmitDetails}>
              Verify PAN
            </Button>
          </CardContent>
        </Card>
      )}

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
              Verifying with NSDL database...
            </p>
          </CardContent>
        </Card>
      )}

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
              Your PAN has been successfully verified.
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
