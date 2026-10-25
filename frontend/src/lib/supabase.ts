/**
 * Sagarvani — Supabase Browser Client
 *
 * Initialised once and exported as a singleton.
 * Uses NEXT_PUBLIC_ prefixed env vars so they are exposed to the browser.
 * The publishable key is safe to embed in client-side code; it is NOT a
 * service_role or secret key.
 *
 * AGENTS.md rules:
 *  - Never put SUPABASE_SECRET_KEY in browser code or NEXT_PUBLIC_ vars.
 *  - A signed-in user access token (not the publishable key) must be sent
 *    in Authorization: Bearer <token> for server-side identity checks.
 */
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabasePublishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl) {
  throw new Error(
    "Missing env var NEXT_PUBLIC_SUPABASE_URL. " +
      "Add it to frontend/.env.local and restart the dev server."
  );
}
if (!supabasePublishableKey) {
  throw new Error(
    "Missing env var NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY. " +
      "Add it to frontend/.env.local and restart the dev server."
  );
}

export const supabase = createClient(supabaseUrl, supabasePublishableKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
