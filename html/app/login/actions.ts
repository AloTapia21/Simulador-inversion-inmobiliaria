"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

function credentials(formData: FormData) {
  return {
    email: String(formData.get("email") ?? "").trim(),
    password: String(formData.get("password") ?? ""),
  };
}

export async function login(formData: FormData) {
  const data = credentials(formData);
  if (!data.email || !data.password) redirect("/login?error=Completa+tu+correo+y+contraseña");

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword(data);
  if (error) redirect("/login?error=No+fue+posible+iniciar+sesión");
  redirect("/");
}

export async function signup(formData: FormData) {
  const data = credentials(formData);
  if (!data.email || data.password.length < 8) {
    redirect("/login?error=Usa+un+correo+válido+y+una+contraseña+de+8+caracteres");
  }

  const supabase = await createClient();
  const { data: result, error } = await supabase.auth.signUp(data);
  if (error) redirect("/login?error=No+fue+posible+crear+la+cuenta");
  if (result.session) redirect("/");
  redirect("/login?message=Revisa+tu+correo+para+confirmar+la+cuenta");
}
