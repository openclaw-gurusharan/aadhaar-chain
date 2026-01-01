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
    { href: '/', label: 'Home' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/identity/create', label: 'Create Identity' },
    { href: '/verify/aadhaar', label: 'Verify Aadhaar' },
    { href: '/verify/pan', label: 'Verify PAN' },
    { href: '/credentials', label: 'Credentials' },
    { href: '/settings', label: 'Settings' },
  ];

  const handleNavClick = () => setOpen(false);

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50 pointer-events-none">
      <div className="container mx-auto px-4 pointer-events-auto">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8 pointer-events-auto">
            <Link href="/" className="text-xl font-bold tracking-tight" onClick={handleNavClick}>
              Identity Agent
            </Link>
            <div className="hidden md:flex items-center gap-6">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm transition-colors hover:text-foreground/80 ${
                    pathname === link.href
                      ? 'text-foreground font-medium'
                      : 'text-foreground/60'
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
                <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[280px] sm:w-[320px]">
                <SheetHeader>
                  <SheetTitle>Navigation</SheetTitle>
                  <SheetDescription>
                    Quick access to all pages
                  </SheetDescription>
                </SheetHeader>
                <nav className="mt-8 flex flex-col gap-4">
                  {links.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={handleNavClick}
                      className={`text-lg transition-colors hover:text-primary py-2 border-b border-border/50 last:border-0 ${
                        pathname === link.href
                          ? 'text-primary font-semibold'
                          : 'text-foreground/70'
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
