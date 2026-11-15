import { createClient } from "./server";

export async function authenticatedClient() {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  const claims = data?.claims;
  const ownerId = claims?.sub;
  if (error || !ownerId) return null;
  const email = typeof claims.email === "string" ? claims.email : "";
  const displayName = typeof claims.user_metadata?.full_name === "string"
    ? claims.user_metadata.full_name
    : email || "Propietario";
  return { supabase, ownerId, email, displayName };
}
