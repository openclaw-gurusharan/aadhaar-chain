'use client';

import { useEffect, useState } from 'react';

export const Navbar = () => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check if wallet is connected (you can integrate with actual wallet adapter)
    const checkWallet = () => {
      // Placeholder for wallet connection check
      setIsConnected(false);
    };
    checkWallet();
  }, []);

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

          {/* Connect Wallet Button */}
          <button
            onClick={() => setIsConnected(!isConnected)}
            className="px-6 py-2 bg-[var(--charcoal)] text-[var(--cream)] font-medium rounded-sm hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 active:translate-y-0"
          >
            {isConnected ? 'Connected' : 'Connect Wallet'}
          </button>
        </div>
      </div>
    </nav>
  );
};
