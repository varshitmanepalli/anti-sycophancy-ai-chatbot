import { NextResponse } from "next/server";

/** Lightweight health check for Docker and load balancers. */
export async function GET() {
  return NextResponse.json(
    {
      status: "ok",
      service: "frontend",
      timestamp: new Date().toISOString(),
    },
    {
      headers: {
        "Cache-Control": "no-store, no-cache, must-revalidate",
      },
    },
  );
}
