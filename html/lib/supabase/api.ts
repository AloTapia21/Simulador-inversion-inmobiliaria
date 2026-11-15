import { createClient } from "./server";

export async function authenticatedClient() {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getClaims();
  const ownerId = data?.claims?.sub;
  if (error || !ownerId) return null;
  return { supabase, ownerId };
}
