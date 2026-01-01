'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { useConnection } from '@solana/wallet-adapter-react';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

export function WalletInfo() {
  const { publicKey, connected } = useWallet();
  const { connection } = useConnection();
  const [balance, setBalance] = useState<number>(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (publicKey && connected) {
      setLoading(true);
      connection.getBalance(publicKey)
        .then((bal) => {
          setBalance(bal / LAMPORTS_PER_SOL);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [publicKey, connected, connection]);

  if (!connected) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Wallet Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Not connected</p>
        </CardContent>
      </Card>
    );
  }

  const address = publicKey?.toBase58() || '';
  const shortAddress = address.slice(0, 4) + '...' + address.slice(-4);

  return (
    <Card className="metric-card">
      <CardHeader>
        <CardTitle className="text-lg">Wallet Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="data-row">
          <span className="data-label">Address</span>
          <span className="data-value text-primary cursor-pointer" title={address}>
            {shortAddress}
          </span>
        </div>
        <div className="data-row">
          <span className="data-label">Balance</span>
          <span className="metric-value text-2xl">
            {loading ? '...' : balance.toFixed(4)} <span className="text-sm text-muted-foreground">SOL</span>
          </span>
        </div>
        <div className="data-row">
          <span className="data-label">Status</span>
          <div className="flex items-center gap-2">
            <span className="status-dot-success" />
            <span className="text-success text-sm font-medium">Connected</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
