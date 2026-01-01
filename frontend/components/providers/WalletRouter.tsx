'use client';

import { useEffect } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { useRouter, usePathname } from 'next/navigation';

// Routes that require wallet connection
const PROTECTED_ROUTES = [
  '/dashboard',
  '/credentials',
  '/identity',
  '/verify',
  '/settings',
];

// Public routes where wallet connection should redirect to dashboard
const PUBLIC_ROUTES = [
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
    const isPublicRoute = PUBLIC_ROUTES.includes(pathname);

    if (connected && isPublicRoute) {
      // Wallet connected on public route → redirect to dashboard
      router.push('/dashboard');
    } else if (!connected && isProtectedRoute) {
      // Wallet disconnected on protected route → redirect to landing
      router.push('/');
    }
  }, [connected, pathname, router]);

  return null;
}
