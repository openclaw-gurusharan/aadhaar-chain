'use client';

import { useEffect, useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletInfo } from '@/components/wallet/WalletInfo';
import { IdentityCard } from '@/components/identity/IdentityCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';

export default function DashboardPage() {
  const { connected } = useWallet();
  const [hasIdentity, setHasIdentity] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        {connected && (
          <div className="flex gap-3">
            <Button variant="outline" asChild>
              <Link href="/credentials">View Credentials</Link>
            </Button>
            <Button asChild>
              <Link href="/identity/create">Create Identity</Link>
            </Button>
          </div>
        )}
      </div>

      {!connected && (
        <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <CardHeader>
            <CardTitle className="text-yellow-800 dark:text-yellow-200">Wallet Required</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-yellow-700 dark:text-yellow-300">
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
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex-col" asChild>
              <Link href="/verify/aadhaar">
                <span className="text-2xl mb-1">📄</span>
                Verify Aadhaar
              </Link>
            </Button>
            <Button variant="outline" className="h-20 flex-col" asChild>
              <Link href="/verify/pan">
                <span className="text-2xl mb-1">💳</span>
                Verify PAN
              </Link>
            </Button>
            <Button variant="outline" className="h-20 flex-col" asChild>
              <Link href="/credentials">
                <span className="text-2xl mb-1">🔐</span>
                Credentials
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
