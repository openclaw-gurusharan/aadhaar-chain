'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { useWalletModal } from '@solana/wallet-adapter-react-ui';
import { useCallback, useEffect, useMemo } from 'react';
import { useWalletStore } from '@/stores/wallet';
import { Button } from '@/components/ui/button';
import { Connection, PublicKey } from '@solana/web3.js';
import { SOLANA_RPC_URL } from '@/lib/wallet';

export function WalletConnectionButton() {
  const { publicKey, disconnect, connected } = useWallet();
  const { setVisible } = useWalletModal();
  const { address, setAddress, setBalance, setConnected, fetchBalance } = useWalletStore();

  useEffect(() => {
    setConnected(connected);
    setAddress(publicKey?.toBase58() ?? null);
  }, [connected, publicKey, setConnected, setAddress]);

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

  const handleClick = useCallback(() => {
    if (connected) {
      disconnect();
    } else {
      setVisible(true);
    }
  }, [connected, disconnect, setVisible]);

  const shortenedAddress = useMemo(() => {
    if (!address) return '';
    return `${address.slice(0, 4)}...${address.slice(-4)}`;
  }, [address]);

  const balance = useWalletStore((state) => state.balance);

  return (
    <div className="flex items-center gap-3">
      {connected && (
        <div className="text-sm text-muted-foreground">
          {balance.toFixed(4)} SOL
        </div>
      )}
      <Button onClick={handleClick} variant={connected ? 'outline' : 'default'}>
        {connected ? shortenedAddress : 'Connect Wallet'}
      </Button>
    </div>
  );
}
