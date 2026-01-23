'use client';

import { useEffect, useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useSearchParams, useRouter } from 'next/navigation';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { authApi } from '@/lib/api';

export default function LoginPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { publicKey, connected } = useWallet();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const returnUrl = searchParams.get('return') || searchParams.get('returnUrl') || '/';

  useEffect(() => {
    // Auto-login when wallet connects
    const handleLogin = async () => {
      if (connected && publicKey) {
        setIsLoading(true);
        setError(null);

        try {
          await authApi.login({
            wallet_address: publicKey.toString(),
          });

          // Redirect back to the calling app
          window.location.href = returnUrl;
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Login failed');
          setIsLoading(false);
        }
      }
    };

    handleLogin();
  }, [connected, publicKey, returnUrl]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-primary/10">
      <div className="max-w-md w-full mx-4">
        <div className="bg-card rounded-lg shadow-lg p-8 border">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">Identity Portal</h1>
            <p className="text-muted-foreground">
              Sign in to access all aadharcha.in applications
            </p>
          </div>

          {/* Wallet Connect */}
          <div className="space-y-4">
            {!connected ? (
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-4">
                  Connect your wallet to continue
                </p>
                <WalletMultiButton className="w-full" />
              </div>
            ) : isLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4" />
                <p className="text-sm text-muted-foreground">
                  Signing in...
                </p>
              </div>
            ) : error ? (
              <div className="bg-destructive/10 text-destructive p-4 rounded-md">
                <p className="text-sm font-medium">Sign In Failed</p>
                <p className="text-xs mt-1">{error}</p>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-sm text-green-600">
                  ✓ Connected as {publicKey?.toString().slice(0, 8)}...
                </p>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="mt-8 pt-6 border-t text-center text-xs text-muted-foreground">
            <p>
              Your single sign-on session will work across:
            </p>
            <ul className="mt-2 space-y-1">
              <li>• aadharcha.in</li>
              <li>• flatwatch.aadharcha.in</li>
              <li>• ondcbuyer.aadharcha.in</li>
              <li>• ondcseller.aadharcha.in</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
