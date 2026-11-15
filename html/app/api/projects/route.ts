import { NextRequest, NextResponse } from "next/server";
import type { Project } from "@/lib/investment";
import { apiError, coerceProject, sanitizeProject } from "@/lib/investment-api";
import { authenticatedClient } from "@/lib/supabase/api";
import { isSupabaseConfigured } from "@/lib/supabase/config";

export const dynamic = "force-dynamic";

export async function GET() {
  if (!isSupabaseConfigured()) return NextResponse.json({ configured: false, projects: [] });
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const { data, error } = await auth.supabase.from("investment_projects").select("*").order("created_at", { ascending: false });
    if (error) throw error;
    return NextResponse.json({ configured: true, projects: (data as Project[]).map(coerceProject) });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const body = await request.json();
    const { data, error } = await auth.supabase
      .from("investment_projects")
      .insert({ ...sanitizeProject(body), owner_id: auth.ownerId })
      .select("*")
      .single();
    if (error) throw error;
    const { error: memberError } = await auth.supabase.from("investment_project_members").insert({
      project_id: data.id,
      user_id: auth.ownerId,
      invited_email: auth.email || null,
      display_name: auth.displayName,
      role: "owner",
      ownership_percentage: 100,
      created_by: auth.ownerId,
    });
    if (memberError) {
      await auth.supabase.from("investment_projects").delete().eq("id", data.id);
      throw memberError;
    }
    return NextResponse.json({ project: coerceProject(data as Project) }, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
