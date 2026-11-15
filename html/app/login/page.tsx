import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/config";
import { Building2, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { login, signup } from "./actions";

type Props = { searchParams: Promise<{ error?: string; message?: string }> };

export default async function LoginPage({ searchParams }: Props) {
  if (!isSupabaseConfigured()) redirect("/");
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  if (data?.claims?.sub) redirect("/");
  const params = await searchParams;

  return (
    <main className="login-shell">
      <section className="login-brand">
        <div className="login-brandmark"><Building2 size={28} /></div>
        <span className="panel-kicker">Control inmobiliario</span>
        <h1>Convierte la estimación en una inversión medible.</h1>
        <p>Compara cada mes el flujo esperado con el real, registra todos los desembolsos y conserva el historial de cada propiedad.</p>
        <div className="login-points">
          <span><i>01</i> Proyección y resultado real</span>
          <span><i>02</i> Datos privados en Supabase</span>
          <span><i>03</i> Diseñado para computador y teléfono</span>
        </div>
      </section>

      <section className="login-card">
        <div className="login-lock"><LockKeyhole size={19} /></div>
        <span className="panel-kicker">Tu portafolio privado</span>
        <h2>Entra a VETA</h2>
        <p>Usa tu correo para abrir el mismo portafolio desde cualquier dispositivo.</p>
        {params.error && <div className="auth-message error" role="alert">{params.error}</div>}
        {params.message && <div className="auth-message success" role="status">{params.message}</div>}
        <form className="login-form">
          <label>Correo electrónico<input name="email" type="email" autoComplete="email" required placeholder="tu@correo.cl" /></label>
          <label>Contraseña<input name="password" type="password" autoComplete="current-password" minLength={8} required placeholder="Mínimo 8 caracteres" /></label>
          <button className="button primary large" formAction={login}>Iniciar sesión</button>
          <button className="button ghost large" formAction={signup}>Crear cuenta</button>
        </form>
        <small>Al crear una cuenta, tus datos quedan aislados mediante políticas de seguridad por usuario.</small>
        <Link href="/" className="login-back">Volver al inicio</Link>
      </section>
    </main>
  );
}
