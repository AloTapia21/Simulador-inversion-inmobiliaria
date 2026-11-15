import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

type UfResponse = {
  serie?: Array<{ fecha: string; valor: number }>;
};

export async function GET(request: NextRequest) {
  const date = request.nextUrl.searchParams.get("date");
  if (date && !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return NextResponse.json({ error: "Fecha inválida" }, { status: 400 });
  }
  const endpoint = date
    ? `https://mindicador.cl/api/uf/${date.slice(8, 10)}-${date.slice(5, 7)}-${date.slice(0, 4)}`
    : "https://mindicador.cl/api/uf";
  try {
    const response = await fetch(endpoint, { next: { revalidate: date ? 86400 * 30 : 3600 } });
    if (!response.ok) throw new Error(`UF respondió ${response.status}`);
    const payload = await response.json() as UfResponse;
    const item = payload.serie?.[0];
    if (!item || !Number.isFinite(Number(item.valor))) {
      return NextResponse.json({ error: "No hay valor UF para esa fecha" }, { status: 404 });
    }
    return NextResponse.json({
      value: Number(item.valor),
      date: item.fecha.slice(0, 10),
      source: "mindicador.cl",
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "No fue posible consultar la UF" }, { status: 502 });
  }
}
