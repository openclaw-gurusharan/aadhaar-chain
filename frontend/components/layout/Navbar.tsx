'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import { usePathname } from 'next/navigation';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { useState } from 'react';

// Loading placeholder for wallet button
function WalletButtonSkeleton() {
  return <div className="h-10 w-32 bg-muted animate-pulse rounded" />;
}

// Dynamically import WalletConnectionButton to skip SSR
// This prevents hydration mismatches with @solana/wallet-adapter-react-ui
const WalletConnectionButton = dynamic(
  () => import('@/components/wallet/WalletButton').then(mod => ({ default: mod.WalletConnectionButton })),
  {
    ssr: false,
    loading: () => <WalletButtonSkeleton />
  }
);

export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/identity/create', label: 'Create Identity' },
    { href: '/verify/aadhaar', label: 'Verify Aadhaar' },
    { href: '/verify/pan', label: 'Verify PAN' },
    { href: '/credentials', label: 'Credentials' },
    { href: '/settings', label: 'Settings' },
  ];

  const handleNavClick = () => setOpen(false);

  return (
    <nav className="border-b border-[var(--charcoal)]/5 bg-[var(--cream)] backdrop-blur-sm sticky top-0 z-50 pointer-events-none">
      <div className="container mx-auto px-4 pointer-events-auto">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8 pointer-events-auto">
            <Link href="/" className="text-lg font-semibold text-[var(--charcoal)] tracking-tight hover:opacity-80 transition-opacity" onClick={handleNavClick}>
              AadhaarChain
            </Link>
            <div className="hidden md:flex items-center gap-6">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm transition-colors duration-200 hover:opacity-80 ${
                    pathname === link.href
                      ? 'text-[var(--charcoal)] font-medium'
                      : 'text-[var(--charcoal)]/60'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4 pointer-events-auto">
            <WalletConnectionButton />
            {/* Mobile menu trigger */}
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden text-[var(--charcoal)] hover:bg-[var(--charcoal)]/5" aria-label="Open menu">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[280px] sm:w-[320px] bg-[var(--cream)] border-[var(--charcoal)]/10">
                <SheetHeader>
                  <SheetTitle className="text-[var(--charcoal)]">Navigation</SheetTitle>
                  <SheetDescription className="text-[var(--charcoal)]/60">
                    Quick access to all pages
                  </SheetDescription>
                </SheetHeader>
                <nav className="mt-8 flex flex-col gap-4">
                  {links.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={handleNavClick}
                      className={`text-base transition-colors duration-200 hover:opacity-80 py-2 border-b border-[var(--charcoal)]/8 last:border-0 ${
                        pathname === link.href
                          ? 'text-[var(--charcoal)] font-semibold'
                          : 'text-[var(--charcoal)]/70'
                      }`}
                    >
                      {link.label}
                    </Link>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
}
