'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { CredentialGrid } from '@/components/credentials/CredentialGrid';
import { FetchCredentialModal } from '@/components/credentials/FetchCredentialModal';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCredentialStore } from '@/stores/credentials';
import { CredentialType } from '@/lib/credentials';
import { credentialsApi } from '@/lib/api';
import type { CredentialResponse } from '@/lib/types';

export default function VerifyPage() {
  const { connected, publicKey } = useWallet();
  const [credentials, setCredentials] = useState<CredentialResponse[]>([]);
  const [error, setError] = useState('');
  const { modalOpen, openModal, closeModal } = useCredentialStore();

  // Get verified credential types
  const verifiedTypes = new Set<CredentialType>(
    credentials.map((c) => c.credential_type as CredentialType)
  );

  // Fetch credentials
  useEffect(() => {
    if (!connected || !publicKey) {
      return;
    }

    let isMounted = true;

    const load = async () => {
      try {
        const walletAddress = publicKey.toString();
        const data = await credentialsApi.getCredentials(walletAddress);
        if (isMounted) {
          setCredentials(data);
          setError('');
        }
      } catch (err: unknown) {
        if (!isMounted) return;
        // Ignore 404 errors (no credentials yet)
        if (err && typeof err === 'object' && 'response' in err) {
          const errorResponse = err as { response?: { status?: number; data?: { message?: string } } };
          if (errorResponse.response?.status !== 404) {
            setError(errorResponse.response?.data?.message || 'Failed to load credentials');
          } else {
            setCredentials([]);
            setError('');
          }
        } else if (err instanceof Error) {
          setError(err.message || 'Failed to load credentials');
        } else {
          setCredentials([]);
          setError('');
        }
      }
    };

    load();

    return () => {
      isMounted = false;
    };
  }, [connected, publicKey]);

  const handleFetch = (type: CredentialType) => {
    openModal(type);
  };

  const handleCloseModal = () => {
    closeModal();
  };

  // Refresh function for after credential is added
  const handleCredentialAdded = useCallback(async () => {
    if (!connected || !publicKey) {
      return;
    }

    try {
      const walletAddress = publicKey.toString();
      const data = await credentialsApi.getCredentials(walletAddress);
      setCredentials(data);
      setError('');
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const errorResponse = err as { response?: { status?: number; data?: { message?: string } } };
        if (errorResponse.response?.status !== 404) {
          setError(errorResponse.response?.data?.message || 'Failed to load credentials');
        }
      } else if (err instanceof Error) {
        setError(err.message || 'Failed to load credentials');
      }
    }
  }, [connected, publicKey]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1>Verify Credentials</h1>
          <p className="text-muted-foreground">
            Fetch and tokenize your government-issued credentials via API Setu
          </p>
        </div>
      </div>

      {!connected && (
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to verify credentials
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

      {connected && (
        <>
          {/* How it works */}
          <Card>
            <CardHeader>
              <CardTitle>How it works</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
                <li>Select a credential type and click &quot;Fetch Credential&quot;</li>
                <li>Enter the required details (e.g., Aadhaar number, PAN number)</li>
                <li>Verify via OTP sent to your Aadhaar-linked mobile number</li>
                <li>Preview the fetched data and confirm to store on blockchain</li>
              </ol>
            </CardContent>
          </Card>

          {/* Available Credentials */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Available Credentials</h2>
            <CredentialGrid verifiedTypes={verifiedTypes} onFetch={handleFetch} />
          </div>
        </>
      )}

      <FetchCredentialModal
        open={modalOpen}
        onClose={handleCloseModal}
        onComplete={handleCredentialAdded}
      />
    </div>
  );
}
