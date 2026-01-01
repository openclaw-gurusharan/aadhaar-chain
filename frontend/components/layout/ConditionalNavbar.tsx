'use client';

import { usePathname } from 'next/navigation';
import { Navbar } from './Navbar';

export const ConditionalNavbar = () => {
  const pathname = usePathname();

  // Hide navbar on landing page
  if (pathname === '/') {
    return null;
  }

  return (
    <>
      <Navbar />
      <div className="border-b" />
    </>
  );
};

export const ConditionalMainWrapper = ({ children }: { children: React.ReactNode }) => {
  const pathname = usePathname();

  // Full-width for landing page
  if (pathname === '/') {
    return <>{children}</>;
  }

  // Container + padding for other pages
  return (
    <main className="container mx-auto px-4 py-8">
      {children}
    </main>
  );
};
