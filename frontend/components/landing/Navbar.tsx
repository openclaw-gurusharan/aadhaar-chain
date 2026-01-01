'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';

// Dynamically import WalletMultiButton to avoid SSR hydration issues
const WalletMultiButton = dynamic(
  () => import('@solana/wallet-adapter-react-ui').then(mod => mod.WalletMultiButton),
  { ssr: false }
);

export const Navbar = () => {
  return (
    <nav className="navbar fixed top-0 left-0 right-0 z-50 bg-[var(--cream)] border-b border-[var(--charcoal)]/5 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-lg font-semibold text-[var(--charcoal)] hover:opacity-80 transition-opacity">
              AadhaarChain
            </Link>
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
