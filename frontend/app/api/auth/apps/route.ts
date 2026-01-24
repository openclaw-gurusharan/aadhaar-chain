import { NextRequest, NextResponse } from 'next/server';

const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const SESSION_COOKIE = 'aadharcha_session';

export async function GET(request: NextRequest) {
  try {
    const sessionCookie = request.cookies.get(SESSION_COOKIE);

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (sessionCookie) {
      headers['Cookie'] = `${SESSION_COOKIE}=${sessionCookie.value}`;
    }

    const response = await fetch(`${GATEWAY_URL}/api/auth/apps`, {
      method: 'GET',
      headers,
    });

    const data = await response.json();
    const nextResponse = NextResponse.json(data, { status: response.status });

    const setCookieHeaders = response.headers.getSetCookie();
    for (const setCookie of setCookieHeaders) {
      nextResponse.headers.append('set-cookie', setCookie);
    }

    return nextResponse;
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to connect to gateway' },
      { status: 500 }
    );
  }
}
