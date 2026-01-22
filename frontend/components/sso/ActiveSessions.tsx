'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useEffect, useState } from 'react';
import { authApi } from '@/lib/api';
import type { SessionInfo } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';

export function ActiveSessions() {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revokingId, setRevokingId] = useState<number | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await authApi.getSessions();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleRevoke = async (sessionId: number) => {
    try {
      setRevokingId(sessionId);
      await authApi.revokeSession(sessionId);
      // Refresh the list
      await fetchSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke session');
    } finally {
      setRevokingId(null);
    }
  };

  const getDeviceName = (userAgent?: string): string => {
    if (!userAgent) return 'Unknown Device';

    // Simple user agent parsing
    if (userAgent.includes('Mobile')) return 'Mobile';
    if (userAgent.includes('Tablet')) return 'Tablet';
    if (userAgent.includes('Chrome')) return 'Chrome (Desktop)';
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) return 'Safari';
    if (userAgent.includes('Firefox')) return 'Firefox';
    if (userAgent.includes('Edge')) return 'Edge';

    return 'Desktop Browser';
  };

  const isCurrentSession = (session: SessionInfo): boolean => {
    // Current session is the one that was most recently active
    // This is a simple heuristic - in production, you'd track the actual current session ID
    return sessions.length > 0 && sessions[0].session_id === session.session_id;
  };

  if (loading) {
    return (
      <Card className="metric-card">
        <CardHeader>
          <CardTitle className="text-lg">Active Sessions</CardTitle>
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
          <CardTitle className="text-lg">Active Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="metric-card">
      <CardHeader>
        <CardTitle className="text-lg">Active Sessions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sessions.length === 0 ? (
          <p className="text-sm text-muted-foreground">No active sessions</p>
        ) : (
          <div className="space-y-3">
            {sessions.map((session) => {
              const deviceName = getDeviceName(session.user_agent);
              const lastActive = formatDistanceToNow(new Date(session.last_active * 1000), {
                addSuffix: true,
              });
              const expiresAt = formatDistanceToNow(new Date(session.expires_at * 1000), {
                addSuffix: true,
              });
              const current = isCurrentSession(session);
              const isRevoking = revokingId === session.session_id;

              return (
                <div
                  key={session.session_id}
                  className="flex items-center justify-between p-3 rounded-lg border bg-card"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-xl">💻</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-sm">{deviceName}</p>
                        {current && (
                          <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Last active {lastActive} • Expires {expiresAt}
                      </p>
                      {session.ip_address && (
                        <p className="text-xs text-muted-foreground">
                          IP: {session.ip_address}
                        </p>
                      )}
                    </div>
                  </div>
                  {!current && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-shrink-0 text-destructive hover:text-destructive"
                      onClick={() => handleRevoke(session.session_id)}
                      disabled={isRevoking}
                    >
                      {isRevoking ? 'Revoking...' : 'Revoke'}
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        )}

        <div className="pt-2 border-t">
          <p className="text-xs text-muted-foreground">
            Sessions are valid for 30 days. Revoke any sessions you don't recognize.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
