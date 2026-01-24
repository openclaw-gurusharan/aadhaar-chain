import { NextRequest, NextResponse } from 'next/server';

const GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const cookies = request.cookies.getAll();
    const cookieHeader = cookies
      .map(c => `${c.name}=${c.value}`)
      .join('; ');

    const response = await fetch(`${GATEWAY_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookieHeader,
      },
      credentials: 'include',
    });

    const data = await response.json();
    const nextResponse = NextResponse.json(data, { status: response.status });

    // Forward set-cookie headers (to clear cookie)
    const setCookieHeader = response.headers.get('set-cookie');
    if (setCookieHeader) {
      nextResponse.headers.set('set-cookie', setCookieHeader);
    }

    return nextResponse;
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to connect to gateway' },
      { status: 500 }
    );
  }
}
