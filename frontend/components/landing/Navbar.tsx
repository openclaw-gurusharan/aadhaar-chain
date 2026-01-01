'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';

export const Navbar = () => {
  const { connected, publicKey } = useWallet();

  return (
    <nav className="navbar fixed top-0 left-0 right-0 z-50 bg-[var(--cream)] border-b border-[var(--charcoal)]/5 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="text-lg font-semibold text-[var(--charcoal)] hover:opacity-80 transition-opacity">
              AadhaarChain
            </a>
          </div>

          {/* Connect Wallet Button - Solana Wallet Adapter */}
          <div className="wallet-button-wrapper">
            <WalletMultiButton />
          </div>
        </div>
      </div>
    </nav>
  );
};
