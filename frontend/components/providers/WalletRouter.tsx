'use client';

import { useEffect } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useRouter, usePathname } from 'next/navigation';

// Routes that require wallet connection (redirect to landing if disconnected)
const PROTECTED_ROUTES = [
  '/dashboard',
  '/credentials',
  '/identity',
  '/settings',
];

// Routes that should redirect to dashboard if wallet is connected
const REDIRECT_TO_DASHBOARD_WHEN_CONNECTED = [
  '/',
];

export function WalletRouter() {
  const { connected } = useWallet();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check if current route requires wallet
    const isProtectedRoute = PROTECTED_ROUTES.some(route =>
      pathname.startsWith(route)
    );
    const shouldRedirectToDashboard = REDIRECT_TO_DASHBOARD_WHEN_CONNECTED.includes(pathname);

    if (connected && shouldRedirectToDashboard) {
      // Wallet connected on landing → redirect to dashboard
      router.push('/dashboard');
    } else if (!connected && isProtectedRoute) {
      // Wallet disconnected on protected route → redirect to landing
      router.push('/');
    }
  }, [connected, pathname, router]);

  return null;
}
