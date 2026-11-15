import { InvestmentApp } from "@/components/investment/investment-app";
import { isSupabaseConfigured } from "@/lib/supabase/config";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function Home() {
  if (!isSupabaseConfigured()) {
    return <InvestmentApp displayName="Modo local" />;
  }

  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const claims = data?.claims;
  if (!claims?.sub) redirect("/login");

  const displayName =
    typeof claims.user_metadata?.full_name === "string"
      ? claims.user_metadata.full_name
      : typeof claims.email === "string"
        ? claims.email
        : "Mi cuenta";
  return <InvestmentApp displayName={displayName} authenticated />;
}
