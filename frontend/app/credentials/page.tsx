'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { credentialsApi } from '@/lib/api';
import type { CredentialResponse } from '@/lib/types';
import { CREDENTIAL_TYPES } from '@/lib/credentials';

export default function CredentialsPage() {
  const { connected, publicKey } = useWallet();
  const router = useRouter();
  const [credentials, setCredentials] = useState<CredentialResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch credentials on mount
  const fetchCredentials = useCallback(async () => {
    if (!connected || !publicKey) {
      setCredentials([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const walletAddress = publicKey.toString();
      const data = await credentialsApi.getCredentials(walletAddress);
      setCredentials(data);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const errorResponse = err as { response?: { status?: number; data?: { message?: string } } };
        if (errorResponse.response?.status === 404) {
          setCredentials([]);
        } else {
          setError(errorResponse.response?.data?.message || 'Failed to load credentials');
        }
      } else if (err instanceof Error) {
        setError(err.message || 'Failed to load credentials');
      } else {
        setCredentials([]);
      }
    } finally {
      setLoading(false);
    }
  }, [connected, publicKey]);

  useEffect(() => {
    fetchCredentials();
  }, [fetchCredentials]);

  const handleAddCredential = () => {
    router.push('/verify');
  };

  // Get credential display info
  const getCredentialDisplay = (type: string) => {
    const normalizedType = type.toLowerCase() as keyof typeof CREDENTIAL_TYPES;
    const config = CREDENTIAL_TYPES[normalizedType];
    return {
      title: config?.title || type.charAt(0).toUpperCase() + type.slice(1),
      icon: config?.icon,
      color: config?.color || 'gray',
    };
  };

  // Format date (handle both timestamps and ISO strings)
  const formatDate = (dateValue: number | string | Date) => {
    const date = typeof dateValue === 'number' ? new Date(dateValue * 1000) : new Date(dateValue);
    return date.toLocaleDateString();
  };

  if (!connected) {
    return (
      <div className="space-y-6">
        <h1>Credentials</h1>
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to view your credentials.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1>Credentials</h1>
          <p className="text-muted-foreground">
            Your verified credentials stored on the blockchain
          </p>
        </div>
        <Button variant="default" onClick={handleAddCredential}>
          Add Credential
        </Button>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50 dark:bg-red-950/20">
          <AlertDescription className="text-red-800 dark:text-red-200">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : credentials.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No Credentials</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              You don&apos;t have any credentials yet. Verify your first government credential to get started.
            </p>
            <Button onClick={handleAddCredential}>Verify Credential</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {credentials.map((cred) => {
            const display = getCredentialDisplay(cred.credential_type);
            const IconComponent = display.icon;
            return (
              <Card key={cred.credential_id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-start gap-3">
                      {IconComponent && (
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                          <IconComponent className="h-5 w-5 text-muted-foreground" />
                        </div>
                      )}
                      <div>
                        <CardTitle className="text-lg">{display.title}</CardTitle>
                        <CardDescription>
                          Issued: {formatDate(cred.issued_at)}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge variant={cred.status === 'revoked' ? 'destructive' : 'default'}>
                      {cred.status === 'revoked' ? 'Revoked' : 'Valid'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Type</span>
                      <span className="font-medium capitalize">{cred.credential_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Credential ID</span>
                      <span className="font-mono text-xs">{cred.credential_id.slice(0, 16)}...</span>
                    </div>
                    {cred.expires_at && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Expires</span>
                        <span>{formatDate(cred.expires_at)}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1" disabled>
                      View Details
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1" disabled>
                      Share
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
