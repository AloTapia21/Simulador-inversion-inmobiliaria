import { NextRequest, NextResponse } from "next/server";
import { apiError } from "@/lib/investment-api";
import { number, type InvestmentMember } from "@/lib/investment";
import { authenticatedClient } from "@/lib/supabase/api";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  const projectId = request.nextUrl.searchParams.get("project_id");
  if (!projectId) return NextResponse.json({ error: "Falta project_id" }, { status: 400 });
  try {
    const { data, error } = await auth.supabase
      .from("investment_project_members")
      .select("id,project_id,user_id,invited_email,display_name,role,ownership_percentage,created_at,updated_at")
      .eq("project_id", projectId)
      .order("created_at", { ascending: true });
    if (error) throw error;
    const { data: project } = await auth.supabase
      .from("investment_projects")
      .select("owner_id")
      .eq("id", projectId)
      .maybeSingle();
    const members = (data as InvestmentMember[]).map((member) => ({
      ...member,
      ownership_percentage: number(member.ownership_percentage),
    }));
    return NextResponse.json({ members, can_manage: project?.owner_id === auth.ownerId });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const body = await request.json() as Record<string, unknown>;
    const projectId = String(body.project_id ?? "");
    const email = String(body.email ?? "").trim().toLowerCase();
    const displayName = String(body.display_name ?? "").trim();
    const ownership = number(body.ownership_percentage);
    const role = body.role === "viewer" ? "viewer" : "editor";
    if (!projectId || !email.includes("@") || !displayName) {
      return NextResponse.json({ error: "Nombre y correo son obligatorios" }, { status: 400 });
    }
    if (ownership < 0 || ownership > 100) {
      return NextResponse.json({ error: "La participación debe estar entre 0% y 100%" }, { status: 400 });
    }
    const { data: existingMembers, error: existingError } = await auth.supabase
      .from("investment_project_members")
      .select("id,role,ownership_percentage")
      .eq("project_id", projectId);
    if (existingError) throw existingError;
    const { data, error } = await auth.supabase
      .from("investment_project_members")
      .insert({
        project_id: projectId,
        invited_email: email,
        display_name: displayName,
        role,
        ownership_percentage: ownership,
        created_by: auth.ownerId,
      })
      .select("id,project_id,user_id,invited_email,display_name,role,ownership_percentage,created_at,updated_at")
      .single();
    if (error) throw error;
    if (existingMembers?.length === 1 && existingMembers[0].role === "owner" && number(existingMembers[0].ownership_percentage) === 100) {
      const { error: rebalanceError } = await auth.supabase
        .from("investment_project_members")
        .update({ ownership_percentage: Math.max(0, 100 - ownership), updated_at: new Date().toISOString() })
        .eq("id", existingMembers[0].id);
      if (rebalanceError) throw rebalanceError;
    }
    return NextResponse.json({ member: { ...data, ownership_percentage: number(data.ownership_percentage) } }, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}

export async function PATCH(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  try {
    const body = await request.json() as Record<string, unknown>;
    const id = String(body.id ?? "");
    const ownership = number(body.ownership_percentage);
    const displayName = String(body.display_name ?? "").trim();
    const { data: existing, error: existingError } = await auth.supabase
      .from("investment_project_members")
      .select("role")
      .eq("id", id)
      .maybeSingle();
    if (existingError) throw existingError;
    if (!existing) return NextResponse.json({ error: "Participante no encontrado" }, { status: 404 });
    const role = existing.role === "owner" ? "owner" : body.role === "viewer" ? "viewer" : "editor";
    if (!id || !displayName || ownership < 0 || ownership > 100) {
      return NextResponse.json({ error: "Datos de participante inválidos" }, { status: 400 });
    }
    const { data, error } = await auth.supabase
      .from("investment_project_members")
      .update({ display_name: displayName, role, ownership_percentage: ownership, updated_at: new Date().toISOString() })
      .eq("id", id)
      .select("id,project_id,user_id,invited_email,display_name,role,ownership_percentage,created_at,updated_at")
      .single();
    if (error) throw error;
    return NextResponse.json({ member: { ...data, ownership_percentage: number(data.ownership_percentage) } });
  } catch (error) {
    return apiError(error);
  }
}

export async function DELETE(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  const id = request.nextUrl.searchParams.get("id");
  if (!id) return NextResponse.json({ error: "Falta id" }, { status: 400 });
  try {
    const { error } = await auth.supabase.from("investment_project_members").delete().eq("id", id).neq("role", "owner");
    if (error) throw error;
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return apiError(error);
  }
}
