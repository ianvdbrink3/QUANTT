import { NextRequest, NextResponse } from "next/server";
import {
  validateForwardRequest,
  loadForwardState,
} from "@/lib/portfolio-forward-local.mjs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: NextRequest) {
  try {
    validateForwardRequest(
      request.url,
      request.headers.get("origin"),
      process.env.NODE_ENV === "production",
    );
  } catch {
    return NextResponse.json({ error: "LOCAL_ONLY" }, { status: 403 });
  }
  try {
    return NextResponse.json(await loadForwardState(), {
      headers: {
        "Cache-Control": "no-store, private",
        "X-Content-Type-Options": "nosniff",
        Vary: "Origin",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "LOCAL_AGENT_NOT_STARTED" },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}
