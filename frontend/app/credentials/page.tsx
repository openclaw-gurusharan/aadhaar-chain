'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export default function CredentialsPage() {
  const { connected } = useWallet();

  // Placeholder credentials data
  const credentials = [
    {
      id: 'cred-001',
      type: 'Aadhaar Verification',
      issuer: 'UIDAI',
      issuedAt: '2024-01-15',
      status: 'valid',
    },
    {
      id: 'cred-002',
      type: 'PAN Verification',
      issuer: 'Income Tax Department',
      issuedAt: '2024-01-16',
      status: 'valid',
    },
  ];

  if (!connected) {
    return (
      <div className="space-y-6">
        <h1>Credentials</h1>
        <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <CardContent className="pt-6">
            <p className="text-yellow-800 dark:text-yellow-200">
              Please connect your wallet to view your credentials.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1>Credentials</h1>
        <Button variant="outline">Add Credential</Button>
      </div>

      {credentials.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No Credentials</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              You don&apos;t have any credentials yet. Complete a verification to earn your first credential.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {credentials.map((cred) => (
            <Card key={cred.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{cred.type}</CardTitle>
                    <CardDescription>Issued by {cred.issuer}</CardDescription>
                  </div>
                  <Badge variant={cred.status === 'valid' ? 'default' : 'destructive'}>
                    {cred.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Issued</span>
                    <span>{new Date(cred.issuedAt).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">ID</span>
                    <span className="font-mono text-xs">{cred.id}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    View
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Share
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
