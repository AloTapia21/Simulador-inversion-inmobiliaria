import { NextRequest, NextResponse } from "next/server";
import type { MonthlyRecord } from "@/lib/investment";
import { apiError, coerceRecord, sanitizeRecord } from "@/lib/investment-api";
import { authenticatedClient } from "@/lib/supabase/api";
import { isSupabaseConfigured } from "@/lib/supabase/config";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  if (!isSupabaseConfigured()) return NextResponse.json({ configured: false, records: [] });
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  const projectId = request.nextUrl.searchParams.get("project_id");
  if (!projectId) return NextResponse.json({ error: "Falta project_id" }, { status: 400 });
  try {
    const { data, error } = await auth.supabase
      .from("investment_monthly_records")
      .select("*")
      .eq("project_id", projectId)
      .order("period", { ascending: true });
    if (error) throw error;
    return NextResponse.json({ configured: true, records: (data as MonthlyRecord[]).map(coerceRecord) });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const body = await request.json();
    const payload = sanitizeRecord(body);
    const { data: project, error: projectError } = await auth.supabase
      .from("investment_projects")
      .select("id")
      .eq("id", payload.project_id)
      .maybeSingle();
    if (projectError) throw projectError;
    if (!project) return NextResponse.json({ error: "Proyecto no encontrado" }, { status: 404 });

    const { data, error } = await auth.supabase
      .from("investment_monthly_records")
      .upsert(
        { ...payload, owner_id: auth.ownerId, updated_at: new Date().toISOString() },
        { onConflict: "project_id,period" },
      )
      .select("*")
      .single();
    if (error) throw error;
    return NextResponse.json({ record: coerceRecord(data as MonthlyRecord) }, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
