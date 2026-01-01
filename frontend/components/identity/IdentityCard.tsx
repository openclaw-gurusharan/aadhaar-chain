'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useWallet } from '@solana/wallet-adapter-react';
import { useEffect, useState } from 'react';

interface Identity {
  did: string;
  reputation: number;
}

export function IdentityCard() {
  const { publicKey, connected } = useWallet();
  const [identity] = useState<Identity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!connected) {
      return;
    }
    // TODO: Fetch identity from Solana program
    // For now, show placeholder
  }, [publicKey, connected]);

  // Set loading to false when not connected or after effect runs
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(false);
  }, [connected]);

  if (loading) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Identity Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
            <span className="text-muted-foreground text-sm">Loading...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!identity) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Identity Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="status-dot-muted" />
            <span className="text-sm">No identity found</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Create your decentralized identity to get started.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="metric-card">
      <CardHeader>
        <CardTitle className="text-lg">Identity Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="data-row">
          <span className="data-label">DID</span>
          <span className="data-value">{identity.did}</span>
        </div>

        <div className="card-section">
          <p className="data-label mb-2">Verifications</p>
          <div className="flex flex-wrap gap-2">
            <Badge className="badge-verified">Aadhaar</Badge>
            <Badge className="badge-verified">PAN</Badge>
          </div>
        </div>

        <div className="data-row">
          <span className="data-label">Reputation</span>
          <span className="metric-value text-xl">{identity.reputation}</span>
        </div>
      </CardContent>
    </Card>
  );
}
