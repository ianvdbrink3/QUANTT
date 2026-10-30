import { NextResponse, type NextRequest } from 'next/server';

// Append-only entry point: all frozen research pages retain their exact source.
// This read-only redirect has no broker credentials, webhooks or order handling.
export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL(request.nextUrl.pathname === '/' ? '/portfolio-os' : '/research/prop-firm', request.url), 307);
}

export const config = { matcher: ['/', '/research'] };
