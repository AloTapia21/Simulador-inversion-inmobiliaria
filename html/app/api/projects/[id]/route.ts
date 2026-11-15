import { NextRequest, NextResponse } from "next/server";
import type { Project } from "@/lib/investment";
import { apiError, coerceProject, sanitizeProject } from "@/lib/investment-api";
import { authenticatedClient } from "@/lib/supabase/api";

type Context = { params: Promise<{ id: string }> };

export async function PATCH(request: NextRequest, { params }: Context) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const { id } = await params;
    const body = await request.json();
    const { data, error } = await auth.supabase
      .from("investment_projects")
      .update({ ...sanitizeProject(body), updated_at: new Date().toISOString() })
      .eq("id", id)
      .select("*")
      .maybeSingle();
    if (error) throw error;
    if (!data) return NextResponse.json({ error: "Proyecto no encontrado" }, { status: 404 });
    return NextResponse.json({ project: coerceProject(data as Project) });
  } catch (error) {
    return apiError(error);
  }
}

export async function DELETE(_request: NextRequest, { params }: Context) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const { id } = await params;
    const { error } = await auth.supabase.from("investment_projects").delete().eq("id", id);
    if (error) throw error;
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return apiError(error);
  }
}
