// Client-side API calls ("use client" components only). Never import
// lib/supabase/server here — it touches next/headers, which breaks the
// client build even behind a runtime typeof-window check, because webpack
// still has to include the module in this file's bundle graph. Server
// Components use lib/api-server.ts instead.
import { createClient } from "@/lib/supabase/client";
import { createApiClient, ApiError } from "@/lib/api-core";

export { ApiError };

async function getAccessToken(): Promise<string | undefined> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token;
}

export const api = createApiClient(getAccessToken);
