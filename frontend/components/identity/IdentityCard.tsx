'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useWallet } from '@solana/wallet-adapter-react';
import { useEffect, useState } from 'react';

export function IdentityCard() {
  const { publicKey } = useWallet();
  const [identity, setIdentity] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch identity from Solana program
    // For now, show placeholder
    setLoading(false);
  }, [publicKey]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Identity Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!identity) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Identity Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">No identity found</p>
          <p className="text-sm text-muted-foreground">
            Create your decentralized identity to get started.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Identity Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-sm text-muted-foreground">DID</p>
          <p className="font-mono text-sm">{identity.did}</p>
        </div>

        <div>
          <p className="text-sm text-muted-foreground mb-2">Verifications</p>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">Aadhaar</Badge>
            <Badge variant="outline">PAN</Badge>
          </div>
        </div>

        <div className="flex justify-between">
          <span className="text-sm text-muted-foreground">Reputation</span>
          <span className="font-semibold">{identity.reputation}</span>
        </div>
      </CardContent>
    </Card>
  );
}
