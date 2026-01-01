'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { useWalletStore } from '@/stores/wallet';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function WalletInfo() {
  const { publicKey } = useWallet();
  const { address, balance, isConnected } = useWalletStore();

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Wallet Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Not connected</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wallet Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Address:</span>
          <span className="font-mono text-sm">{address}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Balance:</span>
          <span className="font-semibold">{balance.toFixed(4)} SOL</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Status:</span>
          <span className="text-green-600">Connected</span>
        </div>
      </CardContent>
    </Card>
  );
}
