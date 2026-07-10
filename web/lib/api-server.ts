// Server-side API calls (Server Components only). Never import this from a
// "use client" file — it touches next/headers via lib/supabase/server,
// which fails the client build. Client components use lib/api.ts instead.
import { createClient } from "@/lib/supabase/server";
import { createApiClient, ApiError } from "@/lib/api-core";

export { ApiError };

async function getAccessToken(): Promise<string | undefined> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token;
}

export const apiServer = createApiClient(getAccessToken);
