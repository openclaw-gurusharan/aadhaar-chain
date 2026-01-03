'use client';

import { CredentialCard } from './CredentialCard';
import { CredentialType } from '@/lib/credentials';

interface CredentialGridProps {
  verifiedTypes: Set<CredentialType>;
  onFetch: (type: CredentialType) => void;
}

export function CredentialGrid({ verifiedTypes, onFetch }: CredentialGridProps) {
  const types: CredentialType[] = ['aadhaar', 'pan', 'dl', 'land', 'education'];

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      {types.map((type) => (
        <CredentialCard
          key={type}
          type={type}
          isVerified={verifiedTypes.has(type)}
          onFetch={onFetch}
        />
      ))}
    </div>
  );
}
