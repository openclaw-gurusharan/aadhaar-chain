'use client';

import Link from 'next/link';
import { WalletConnectionButton } from '@/components/wallet/WalletButton';
import { usePathname } from 'next/navigation';

export function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Home' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/identity/create', label: 'Create Identity' },
    { href: '/verify/aadhaar', label: 'Verify Aadhaar' },
    { href: '/credentials', label: 'Credentials' },
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-bold">
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
          <WalletConnectionButton />
        </div>
      </div>
    </nav>
  );
}
