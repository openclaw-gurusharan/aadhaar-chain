'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function SettingsPage() {
  const { connected, publicKey } = useWallet();

  const handleExportData = () => {
    // TODO: Implement data export (GDPR compliance)
    alert('Data export feature coming soon');
  };

  const handleDeleteIdentity = () => {
    if (confirm('Are you sure you want to delete your identity? This action cannot be undone.')) {
      // TODO: Implement identity deletion
      alert('Identity deletion feature coming soon');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>

      {!connected && (
        <Alert className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">
            Please connect your wallet to access settings
          </AlertDescription>
        </Alert>
      )}

      {connected && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Wallet Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Address</span>
                <span className="font-mono text-sm">{publicKey?.toBase58()}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recovery Settings</CardTitle>
              <CardDescription>
                Set up recovery options for your identity
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="recovery-email">Recovery Email</Label>
                <Input id="recovery-email" type="email" placeholder="recovery@example.com" />
              </div>
              <Button>Save Recovery Settings</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Data & Privacy</CardTitle>
              <CardDescription>
                Manage your data and privacy preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">Export Data</p>
                  <p className="text-sm text-muted-foreground">
                    Download all your data (GDPR compliance)
                  </p>
                </div>
                <Button variant="outline" onClick={handleExportData}>
                  Export
                </Button>
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-destructive">Delete Identity</p>
                    <p className="text-sm text-muted-foreground">
                      Permanently delete your identity and all associated data
                    </p>
                  </div>
                  <Button variant="destructive" onClick={handleDeleteIdentity}>
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Network Settings</CardTitle>
              <CardDescription>
                Configure blockchain connection
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>RPC Endpoint</Label>
                <Input
                  value={process.env.NEXT_PUBLIC_SOLANA_RPC_URL || 'https://api.devnet.solana.com'}
                  disabled
                />
              </div>
              <div className="space-y-2">
                <Label>Network</Label>
                <Input value="Devnet" disabled />
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
