import { NextRequest, NextResponse } from "next/server";
import { coerceTransaction, apiError, sanitizeTransaction } from "@/lib/investment-api";
import { number, type InvestmentTransaction } from "@/lib/investment";
import { authenticatedClient } from "@/lib/supabase/api";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  const projectId = request.nextUrl.searchParams.get("project_id");
  if (!projectId) return NextResponse.json({ error: "Falta project_id" }, { status: 400 });
  try {
    const { data, error } = await auth.supabase
      .from("investment_transactions")
      .select("*, investment_transaction_splits(*)")
      .eq("project_id", projectId)
      .order("transaction_date", { ascending: false })
      .order("created_at", { ascending: false });
    if (error) throw error;
    return NextResponse.json({ transactions: (data as InvestmentTransaction[]).map(coerceTransaction) });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  let transactionId: string | null = null;
  try {
    const body = await request.json() as Record<string, unknown>;
    const payload = sanitizeTransaction(body);
    const requestedSplits = Array.isArray(body.splits) ? body.splits as Array<Record<string, unknown>> : [];
    const memberIds = [...new Set(requestedSplits.map((split) => String(split.member_id ?? "")).filter(Boolean))];
    if (!payload.project_id || !payload.transaction_date || !memberIds.length) {
      return NextResponse.json({ error: "Proyecto, fecha y pagadores son obligatorios" }, { status: 400 });
    }
    const { data: members, error: membersError } = await auth.supabase
      .from("investment_project_members")
      .select("id")
      .eq("project_id", payload.project_id)
      .in("id", memberIds);
    if (membersError) throw membersError;
    if ((members ?? []).length !== memberIds.length) {
      return NextResponse.json({ error: "Uno de los participantes no pertenece al proyecto" }, { status: 400 });
    }
    const splits = requestedSplits
      .map((split) => ({ member_id: String(split.member_id ?? ""), amount_clp: number(split.amount_clp) }))
      .filter((split) => split.amount_clp > 0);
    const splitTotal = splits.reduce((sum, split) => sum + split.amount_clp, 0);
    if (Math.abs(splitTotal - payload.amount_clp) > 1) {
      return NextResponse.json({ error: "La distribución debe sumar el monto total" }, { status: 400 });
    }
    const { data: transaction, error } = await auth.supabase
      .from("investment_transactions")
      .insert({ ...payload, created_by: auth.ownerId })
      .select("*")
      .single();
    if (error) throw error;
    transactionId = transaction.id;
    const { error: splitError } = await auth.supabase.from("investment_transaction_splits").insert(
      splits.map((split) => ({
        project_id: payload.project_id,
        transaction_id: transaction.id,
        member_id: split.member_id,
        amount_clp: split.amount_clp,
        amount_uf: split.amount_clp / payload.uf_value,
      })),
    );
    if (splitError) throw splitError;
    const { data: saved, error: reloadError } = await auth.supabase
      .from("investment_transactions")
      .select("*, investment_transaction_splits(*)")
      .eq("id", transaction.id)
      .single();
    if (reloadError) throw reloadError;
    return NextResponse.json({ transaction: coerceTransaction(saved as InvestmentTransaction) }, { status: 201 });
  } catch (error) {
    if (transactionId) await auth.supabase.from("investment_transactions").delete().eq("id", transactionId);
    return apiError(error);
  }
}

export async function DELETE(request: NextRequest) {
  const auth = await authenticatedClient();
  if (!auth) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  const id = request.nextUrl.searchParams.get("id");
  if (!id) return NextResponse.json({ error: "Falta id" }, { status: 400 });
  try {
    const { error } = await auth.supabase.from("investment_transactions").delete().eq("id", id);
    if (error) throw error;
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return apiError(error);
  }
}
