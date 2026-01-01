'use client';

import { WalletProvider } from '@/lib/wallet';
import { WalletRouter } from './WalletRouter';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WalletProvider>
      <WalletRouter />
      {children}
    </WalletProvider>
  );
}
