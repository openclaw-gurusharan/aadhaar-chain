'use client';

import { CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CredentialType, getCredentialConfig } from '@/lib/credentials';

interface CredentialCardProps {
  type: CredentialType;
  isVerified: boolean;
  onFetch: (type: CredentialType) => void;
}

export function CredentialCard({ type, isVerified, onFetch }: CredentialCardProps) {
  const config = getCredentialConfig(type);
  const IconComponent = config.icon;

  return (
    <Card className="group hover:shadow-md transition-all duration-200">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
              <IconComponent className="h-6 w-6 text-muted-foreground" />
            </div>
            <div>
              <CardTitle className="text-lg">{config.title}</CardTitle>
              <CardDescription className="text-sm mt-1">
                {config.description}
              </CardDescription>
            </div>
          </div>
          {isVerified && (
            <span className="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-semibold bg-green-100 text-green-700 rounded">
              <CheckCircle2 className="h-3 w-3" />
              Verified
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <Button
          onClick={() => onFetch(type)}
          variant={isVerified ? 'outline' : 'default'}
          className="w-full"
        >
          {isVerified ? 'View Credential' : 'Fetch Credential'}
        </Button>
      </CardContent>
    </Card>
  );
}
