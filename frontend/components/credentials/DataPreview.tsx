'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2 } from 'lucide-react';
import { CredentialType, PREVIEW_FIELDS, FIELD_LABELS } from '@/lib/credentials';

interface DataPreviewProps {
  data: Record<string, unknown>;
  credentialType: CredentialType;
  onConfirm: () => Promise<void>;
  onEdit: () => void;
  loading?: boolean;
  disabled?: boolean;
}

export function DataPreview({
  data,
  credentialType,
  onConfirm,
  onEdit,
  loading = false,
  disabled = false,
}: DataPreviewProps) {
  const fields = PREVIEW_FIELDS[credentialType];

  return (
    <div className="space-y-4">
      <Alert className="border-blue-200 bg-blue-50 dark:bg-blue-950/20">
        <CheckCircle2 className="h-4 w-4" />
        <AlertDescription className="text-blue-800 dark:text-blue-200">
          Please review the fetched data before storing on the blockchain
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Fetched Data</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {fields.map((field) => {
            const value = data[field];
            const label = FIELD_LABELS[field] || field;

            return (
              <div
                key={field}
                className="flex justify-between items-start py-2 border-b last:border-0"
              >
                <span className="text-sm text-muted-foreground font-medium">
                  {label}
                </span>
                <span className="text-sm font-medium text-right max-w-[60%] break-words">
                  {value !== undefined && value !== null ? String(value) : '-'}
                </span>
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
        <AlertDescription className="text-yellow-800 dark:text-yellow-200 text-sm">
          <strong>Note:</strong> Once confirmed, this data will be stored as a hash commitment
          on the blockchain. You can grant selective access to services without revealing
          the full data.
        </AlertDescription>
      </Alert>

      <div className="flex gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={onEdit}
          disabled={disabled || loading}
          className="flex-1"
        >
          Edit
        </Button>
        <Button
          type="button"
          onClick={onConfirm}
          disabled={disabled || loading}
          className="flex-1"
        >
          {loading ? 'Storing...' : 'Confirm & Store'}
        </Button>
      </div>
    </div>
  );
}
