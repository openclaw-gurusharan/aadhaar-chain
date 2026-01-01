'use client';

import { useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useRouter } from 'next/navigation';

export default function CreateIdentityPage() {
  const { connected, signMessage } = useWallet();
  const [did, setDid] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!connected) {
      setError('Please connect your wallet first');
      return;
    }

    if (!did.trim()) {
      setError('Please enter a DID identifier');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // TODO: Implement actual Solana transaction
      // 1. Generate DID document
      // 2. Create commitment hash
      // 3. Sign transaction
      // 4. Submit to Solana program

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      alert('Identity created successfully!');
      router.push('/dashboard');
    } catch (err) {
      setError('Failed to create identity. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create Identity</h1>
        <p className="text-muted-foreground">
          Create your decentralized identity on Solana
        </p>
      </div>

      {!connected && (
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to continue
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>DID Configuration</CardTitle>
          <CardDescription>
            Your Decentralized Identifier (DID) will be registered on Solana
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="did">DID Identifier</Label>
              <Input
                id="did"
                placeholder="did:solana:..."
                value={did}
                onChange={(e) => setDid(e.target.value)}
                disabled={!connected || loading}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to auto-generate a DID based on your wallet address
              </p>
            </div>

            {error && (
              <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
                <AlertDescription className="text-red-800 dark:text-red-200">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className="flex gap-3">
              <Button type="submit" disabled={!connected || loading}>
                {loading ? 'Creating...' : 'Create Identity'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setDid(`did:solana:${Date.now()}`)}
                disabled={!connected}
              >
                Auto-Generate
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>What happens next?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>1. Your DID will be registered on Solana blockchain</p>
          <p>2. A commitment hash will be stored on-chain</p>
          <p>3. Your personal data stays encrypted off-chain (IPFS)</p>
          <p>4. You can start adding verifications (Aadhaar, PAN, etc.)</p>
        </CardContent>
      </Card>
    </div>
  );
}
