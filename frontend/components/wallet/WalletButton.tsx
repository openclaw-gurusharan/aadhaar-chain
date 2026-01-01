'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { useEffect } from 'react';
import { useWalletStore } from '@/stores/wallet';
import { Connection } from '@solana/web3.js';
import { SOLANA_RPC_URL } from '@/lib/wallet';

export function WalletConnectionButton() {
  const { publicKey, connected } = useWallet();
  const { address, setAddress, setBalance, setConnected, fetchBalance } = useWalletStore();

  // Sync wallet state with Zustand store
  useEffect(() => {
    setConnected(connected);
    setAddress(publicKey?.toBase58() ?? null);
  }, [connected, publicKey, setConnected, setAddress]);

  // Fetch and track balance
  useEffect(() => {
    if (publicKey) {
      const connection = new Connection(SOLANA_RPC_URL, 'confirmed');
      fetchBalance(connection, publicKey);

      const interval = setInterval(() => {
        fetchBalance(connection, publicKey);
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [publicKey, fetchBalance]);

  const balance = useWalletStore((state) => state.balance);

  return (
    <div className="flex items-center gap-3">
      {connected && (
        <div className="text-sm text-muted-foreground hidden sm:block">
          {balance.toFixed(4)} SOL
        </div>
      )}
      <WalletMultiButton
        style={{
          backgroundColor: '#0052A5',
          color: '#ffffff',
          borderRadius: '0.375rem',
        }}
      />
    </div>
  );
}
