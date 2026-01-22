'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useEffect, useState } from 'react';
import { authApi } from '@/lib/api';
import type { ConnectedAppInfo } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';

// App icons/links mapping
const APP_LINKS: Record<string, string> = {
  flatwatch: 'https://flatwatch.aadharcha.in',
  ondc_buyer: 'https://ondcbuyer.aadharcha.in',
  ondc_seller: 'https://ondcseller.aadharcha.in',
  identity_aadhar: 'https://aadharcha.in',
};

const APP_ICONS: Record<string, string> = {
  flatwatch: '🏠',
  ondc_buyer: '🛒',
  ondc_seller: '🏪',
  identity_aadhar: '🔐',
};

export function ConnectedApps() {
  const [apps, setApps] = useState<ConnectedAppInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchApps() {
      try {
        setLoading(true);
        setError(null);
        const data = await authApi.getConnectedApps();
        setApps(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load apps');
      } finally {
        setLoading(false);
      }
    }

    fetchApps();
  }, []);

  if (loading) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Connected Apps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
            <span className="text-muted-foreground text-sm">Loading...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Connected Apps</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (apps.length === 0) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Connected Apps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            No connected apps yet. Your apps will appear here after you access them.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="metric-card">
      <CardHeader>
        <CardTitle className="text-lg">Connected Apps</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid md:grid-cols-2 gap-3">
          {apps.map((app) => {
            const icon = APP_ICONS[app.app_name] || '🔗';
            const link = APP_LINKS[app.app_name];
            const lastAccess = formatDistanceToNow(new Date(app.last_accessed * 1000), {
              addSuffix: true,
            });

            return (
              <div
                key={app.app_name}
                className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-2xl flex-shrink-0">{icon}</span>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm truncate">{app.display_name}</p>
                    <p className="text-xs text-muted-foreground">Last accessed {lastAccess}</p>
                  </div>
                </div>
                {link && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-shrink-0"
                    asChild
                  >
                    <a
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Open
                    </a>
                  </Button>
                )}
              </div>
            );
          })}
        </div>

        <div className="pt-2 border-t">
          <p className="text-xs text-muted-foreground">
            All apps share your secure login across aadharcha.in
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
