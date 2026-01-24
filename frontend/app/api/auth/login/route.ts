import { NextRequest, NextResponse } from 'next/server';

const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${GATEWAY_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    const nextResponse = NextResponse.json(data, { status: response.status });

    // Forward ALL set-cookie headers from gateway (critical for session)
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
