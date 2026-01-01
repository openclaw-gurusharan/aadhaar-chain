'use client';

import { useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletInfo } from '@/components/wallet/WalletInfo';
import { IdentityCard } from '@/components/identity/IdentityCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function DashboardPage() {
  const { connected } = useWallet();
  const [hasIdentity] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        {connected && (
          <div className="flex gap-3">
            <Button variant="outline" asChild className="border-saffron text-saffron hover:bg-saffron hover:text-saffron-foreground">
              <Link href="/credentials">View Credentials</Link>
            </Button>
            <Button asChild className="btn-primary">
              <Link href="/identity/create">Create Identity</Link>
            </Button>
          </div>
        )}
      </div>

      {!connected && (
        <Card className="border-saffron/30 bg-saffron/5">
          <CardHeader>
            <CardTitle className="text-saffron">Wallet Required</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-saffron/80">
              Please connect your wallet to access the dashboard.
            </p>
          </CardContent>
        </Card>
      )}

      {connected && (
        <div className="grid md:grid-cols-2 gap-6">
          <WalletInfo />
          <IdentityCard />
        </div>
      )}

      {connected && hasIdentity && (
        <Card className="metric-card">
          <CardHeader>
            <CardTitle className="tracking-tight">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex-col hover-lift" asChild>
              <Link href="/verify/aadhaar">
                <span className="text-2xl mb-1">📄</span>
                <span className="text-sm">Verify Aadhaar</span>
              </Link>
            </Button>
            <Button variant="outline" className="h-20 flex-col hover-lift" asChild>
              <Link href="/verify/pan">
                <span className="text-2xl mb-1">💳</span>
                <span className="text-sm">Verify PAN</span>
              </Link>
            </Button>
            <Button variant="outline" className="h-20 flex-col hover-lift" asChild>
              <Link href="/credentials">
                <span className="text-2xl mb-1">🔐</span>
                <span className="text-sm">Credentials</span>
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
