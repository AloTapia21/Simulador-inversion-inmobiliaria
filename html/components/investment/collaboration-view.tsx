"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Calculator,
  HandCoins,
  Landmark,
  Plus,
  RefreshCw,
  Save,
  Trash2,
  TrendingUp,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import {
  buildComparisons,
  currentInvestmentSnapshot,
  dfl2Assessment,
  formatClp,
  formatPercent,
  formatUf,
  memberContributionSummary,
  number,
  plannedAcquisitionSummary,
  transactionCategory,
  TRANSACTION_CATEGORIES,
  type InvestmentMember,
  type InvestmentTransaction,
  type Project,
  type TransactionCategory,
} from "@/lib/investment";

type Props = {
  project: Project;
  cloud: boolean;
  onProjectUpdated: (project: Project) => void;
  onNotice: (message: string) => void;
};

type TransactionDraft = {
  transaction_date: string;
  category: TransactionCategory;
  amount_clp: number;
  uf_value: number;
  allocation: string;
  notes: string;
};

export function CollaborationView({ project, cloud, onProjectUpdated, onNotice }: Props) {
  const [members, setMembers] = useState<InvestmentMember[]>([]);
  const [transactions, setTransactions] = useState<InvestmentTransaction[]>([]);
  const [currentUf, setCurrentUf] = useState(number(project.uf_value));
  const [ufDate, setUfDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [canManage, setCanManage] = useState(false);
  const [busy, setBusy] = useState(false);
  const [transactionOpen, setTransactionOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [marketValueUf, setMarketValueUf] = useState(number(project.current_market_value_uf));
  const [draft, setDraft] = useState<TransactionDraft>(() => emptyTransaction(project));
  const [splitAmounts, setSplitAmounts] = useState<Record<string, number>>({});

  async function loadProjectData() {
    if (!cloud) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const [membersResponse, transactionsResponse, ufResponse] = await Promise.all([
        fetch(`/api/members?project_id=${encodeURIComponent(project.id)}`, { cache: "no-store" }),
        fetch(`/api/transactions?project_id=${encodeURIComponent(project.id)}`, { cache: "no-store" }),
        fetch("/api/uf", { cache: "no-store" }),
      ]);
      if (!membersResponse.ok || !transactionsResponse.ok) throw new Error("No fue posible cargar la inversión compartida");
      const [membersPayload, transactionsPayload] = await Promise.all([
        membersResponse.json(),
        transactionsResponse.json(),
      ]);
      setMembers(membersPayload.members ?? []);
      setCanManage(Boolean(membersPayload.can_manage));
      setTransactions(transactionsPayload.transactions ?? []);
      if (ufResponse.ok) {
        const ufPayload = await ufResponse.json();
        setCurrentUf(number(ufPayload.value));
        setUfDate(String(ufPayload.date ?? ""));
      }
    } catch (error) {
      console.error(error);
      onNotice("No fue posible cargar los participantes o movimientos.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- synchronizes cloud data when the selected project changes
    void loadProjectData();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- project id and storage mode define the remote resource
  }, [project.id, cloud]);

  const snapshot = useMemo(
    () => currentInvestmentSnapshot(project, transactions, currentUf || project.uf_value),
    [project, transactions, currentUf],
  );
  const memberSummary = useMemo(
    () => memberContributionSummary(members, transactions, currentUf || project.uf_value),
    [members, transactions, currentUf, project.uf_value],
  );
  const expectedToDate = useMemo(
    () => buildComparisons(project, []).reduce((sum, month) => sum + month.estimatedCashflow, 0),
    [project],
  );
  const actualAcquisitionGross = transactions
    .filter((item) => item.direction === "expense" && ["down_payment", "closing_costs"].includes(item.category))
    .reduce((sum, item) => sum + item.amount_clp, 0);
  const actualVatRefund = transactions
    .filter((item) => item.direction === "income" && item.category === "iva_refund")
    .reduce((sum, item) => sum + item.amount_clp, 0);
  const actualAcquisitionNet = actualAcquisitionGross - actualVatRefund;
  const acquisition = plannedAcquisitionSummary(project);
  const dfl2 = dfl2Assessment(project);

  function openTransaction(category: TransactionCategory = "mortgage") {
    const next = { ...emptyTransaction(project), category, uf_value: currentUf || project.uf_value, allocation: members[0]?.id ?? "shared" };
    setDraft(next);
    setSplitAmounts(allocate(next.amount_clp, next.allocation, members));
    setTransactionOpen(true);
  }

  function updateAmount(amount: number) {
    setDraft((current) => ({ ...current, amount_clp: amount }));
    setSplitAmounts(allocate(amount, draft.allocation, members));
  }

  function updateAllocation(allocation: string) {
    setDraft((current) => ({ ...current, allocation }));
    setSplitAmounts(allocate(draft.amount_clp, allocation, members));
  }

  async function refreshHistoricalUf() {
    try {
      const response = await fetch(`/api/uf?date=${encodeURIComponent(draft.transaction_date)}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Sin UF");
      const payload = await response.json();
      setDraft((current) => ({ ...current, uf_value: number(payload.value) }));
    } catch {
      onNotice("No encontramos la UF de esa fecha. Puedes ingresarla manualmente.");
    }
  }

  async function saveTransaction(event: FormEvent) {
    event.preventDefault();
    const splits = Object.entries(splitAmounts)
      .map(([member_id, amount_clp]) => ({ member_id, amount_clp: number(amount_clp) }))
      .filter((split) => split.amount_clp > 0);
    const total = splits.reduce((sum, split) => sum + split.amount_clp, 0);
    if (!draft.amount_clp || Math.abs(total - draft.amount_clp) > 1) {
      onNotice("La distribución entre participantes debe sumar el monto total.");
      return;
    }
    setBusy(true);
    try {
      const response = await fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...draft, project_id: project.id, splits }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error ?? "No fue posible guardar");
      setTransactions((current) => [payload.transaction, ...current]);
      setTransactionOpen(false);
      onNotice("Movimiento guardado con su UF y distribución.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No fue posible guardar el movimiento.");
    } finally {
      setBusy(false);
    }
  }

  async function deleteTransaction(id: string) {
    if (!window.confirm("¿Eliminar este movimiento? Esta acción modifica el seguimiento real.")) return;
    const response = await fetch(`/api/transactions?id=${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!response.ok) return onNotice("No fue posible eliminar el movimiento.");
    setTransactions((current) => current.filter((item) => item.id !== id));
    onNotice("Movimiento eliminado.");
  }

  async function saveMarketValue() {
    setBusy(true);
    try {
      const response = await fetch(`/api/projects/${project.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_market_value_uf: marketValueUf }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error ?? "No fue posible guardar");
      onProjectUpdated(payload.project);
      onNotice(marketValueUf > 0 ? "Valor de mercado actualizado." : "Se volvió a la estimación automática del motor.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No fue posible actualizar el valor.");
    } finally {
      setBusy(false);
    }
  }

  async function saveMember(member: InvestmentMember) {
    const response = await fetch("/api/members", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: member.id,
        display_name: member.display_name,
        role: member.role,
        ownership_percentage: member.ownership_percentage,
      }),
    });
    if (!response.ok) return onNotice("No fue posible actualizar la participación.");
    const payload = await response.json();
    setMembers((current) => current.map((item) => item.id === payload.member.id ? payload.member : item));
    onNotice("Participación actualizada.");
  }

  if (!cloud) {
    return <section className="panel collaboration-empty"><Users size={30} /><h2>Activa Supabase para compartir</h2><p>Los participantes, permisos y movimientos compartidos necesitan una sesión privada en la nube.</p></section>;
  }

  return (
    <div className="collaboration-stack">
      <section className="live-value-hero">
        <div>
          <span className="panel-kicker">Patrimonio actualizado</span>
          <h2>{formatClp(snapshot.marketValueClp, true)}</h2>
          <p>{formatUf(snapshot.marketValueUf)} × UF {formatClp(currentUf)} {ufDate ? `al ${formatDate(ufDate)}` : ""}</p>
        </div>
        <div className="live-value-note">
          <Calculator size={18} />
          <span>{project.current_market_value_uf > 0 ? "Usando valor de mercado manual" : "Estimación del motor: UF de compra + plusvalía real"}</span>
        </div>
      </section>

      <section className="kpi-grid collaboration-kpis">
        <MiniKpi icon={<Landmark size={18} />} label="Patrimonio estimado" value={formatClp(snapshot.equity, true)} helper={`Deuda: ${formatClp(snapshot.mortgageBalance, true)}`} />
        <MiniKpi icon={<HandCoins size={18} />} label="Dividendos pagados" value={formatClp(snapshot.mortgagePaid, true)} helper={`Plan a hoy: ${formatClp(snapshot.scheduledMortgagePaid, true)}`} />
        <MiniKpi icon={<TrendingUp size={18} />} label="Flujo operativo real" value={formatClp(snapshot.operatingCashflow, true)} helper={`Modelo: ${formatClp(expectedToDate, true)}`} />
        <MiniKpi icon={<Calculator size={18} />} label="TIR real anualizada" value={snapshot.actualIrr === null ? "Aún no calculable" : formatPercent(snapshot.actualIrr)} helper="Movimientos + patrimonio actual" />
      </section>

      <section className="collaboration-grid">
        <article className="panel value-settings">
          <div className="panel-heading"><div><span className="panel-kicker">Valor actual</span><h2>UF y valorización</h2></div></div>
          <div className="value-settings-body">
            <Metric label="Valor sólo reajustado por UF" value={formatClp(snapshot.ufIndexedPurchaseValueClp)} />
            <Metric label="Estimación motor (UF)" value={formatUf(snapshot.engineValueUf)} />
            <Metric label="Capital amortizado estimado" value={formatClp(snapshot.scheduledPrincipalPaid)} />
            <label className="collaboration-field"><span>Valor de mercado manual (UF)</span><div className="inline-control"><input type="number" min="0" step="0.01" value={marketValueUf} onChange={(event) => setMarketValueUf(number(event.target.value))} /><button className="button primary" onClick={saveMarketValue} disabled={busy}><Save size={15} /> Guardar</button></div><small>Déjalo en 0 para usar la estimación automática. Una tasación o comparables reales son más confiables que reajustar sólo por UF.</small></label>
          </div>
        </article>

        <article className="panel acquisition-card">
          <div className="panel-heading"><div><span className="panel-kicker">Compra</span><h2>Capital realmente aportado</h2></div><button className="text-button" onClick={() => openTransaction("down_payment")}><Plus size={15} /> Registrar aporte</button></div>
          <div className="acquisition-comparison acquisition-detail"><div><span>Pie contractual</span><strong>{formatClp(acquisition.contractualDownPayment)}</strong></div><div><span>Bono pie inmobiliaria</span><strong className="positive-text">−{formatClp(acquisition.downPaymentBonus)}</strong></div><div><span>Pie pagado en caja</span><strong>{formatClp(acquisition.cashDownPayment)}</strong></div><div><span>Gastos de compra</span><strong>+{formatClp(acquisition.closingCosts)}</strong></div><div><span>IVA esperado ({ivaStatusLabel(project.iva_refund_status)})</span><strong className="positive-text">−{formatClp(acquisition.expectedVatRefund)}</strong></div><div className="acquisition-total"><span>Capital neto del plan</span><strong>{formatClp(acquisition.netCapitalAfterRefund)}</strong></div><div><span>Capital real registrado</span><strong>{formatClp(actualAcquisitionNet)}</strong></div><div><span>Diferencia real vs plan</span><strong className={actualAcquisitionNet <= acquisition.netCapitalAfterRefund ? "positive-text" : "negative-text"}>{formatClp(actualAcquisitionNet - acquisition.netCapitalAfterRefund)}</strong></div></div>
          <div className={`tax-status ${dfl2.currentlyExempt ? "eligible" : "review"}`}><strong>{dfl2.currentlyExempt ? "Arriendo exento según escenario DFL2" : dfl2.specialRegimeEligible ? "Revisar régimen DFL2 especial desde 2027" : "Arriendo afecto según tasa configurada"}</strong><span>{project.dfl2_qualified ? `${project.dfl2_property_number}° inmueble · ${project.property_surface_m2} m² · tasa usada ${formatPercent(dfl2.effectiveTaxRate)}` : "Completa los datos DFL2 en Supuestos para estimar el efecto tributario."}</span></div>
        </article>
      </section>

      <section className="panel members-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Copropietarios</span><h2>Participación y aportes</h2></div>{canManage && <button className="button ghost" onClick={() => setInviteOpen(true)}><UserPlus size={15} /> Invitar</button>}</div>
        {Math.abs(members.reduce((sum, member) => sum + member.ownership_percentage, 0) - 100) > 0.01 && <div className="share-warning">Los porcentajes suman {formatPercent(members.reduce((sum, member) => sum + member.ownership_percentage, 0) / 100)}. Ajústalos para representar correctamente la propiedad.</div>}
        <div className="member-cards">
          {memberSummary.map((item) => <article key={item.member.id} className="member-card"><div className="member-avatar">{initials(item.member.display_name)}</div><div className="member-main"><strong>{item.member.display_name}</strong><span>{item.member.invited_email || (item.member.role === "owner" ? "Cuenta propietaria" : "Participante")}</span></div><div className="member-share">{canManage ? <div className="share-input"><input aria-label={`Participación de ${item.member.display_name}`} type="number" min="0" max="100" step="0.1" value={item.member.ownership_percentage} onChange={(event) => setMembers((current) => current.map((member) => member.id === item.member.id ? { ...member, ownership_percentage: number(event.target.value) } : member))} onBlur={() => void saveMember(item.member)} /><span>%</span></div> : <strong>{formatPercent(item.member.ownership_percentage / 100)}</strong>}<span>participación</span></div><div className="member-money"><strong>{formatClp(item.netContributionClp)}</strong><span>{formatUf(item.netContributionUf)} · hoy {formatClp(item.currentEquivalentClp)}</span></div></article>)}
        </div>
      </section>

      <section className="panel transactions-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Caja real auditable</span><h2>Movimientos por persona</h2></div><button className="button primary" onClick={() => openTransaction()}><Plus size={15} /> Nuevo movimiento</button></div>
        {loading ? <div className="collaboration-loading"><RefreshCw className="spin" size={20} /> Cargando movimientos…</div> : transactions.length ? (
          <div className="table-scroll"><table className="data-table transaction-table"><thead><tr><th>Fecha</th><th>Concepto</th><th>Pagado / recibido por</th><th>Monto</th><th>UF histórica</th><th></th></tr></thead><tbody>{transactions.map((transaction) => <tr key={transaction.id}><td><b>{formatDate(transaction.transaction_date)}</b></td><td>{transactionCategory(transaction.category).label}{transaction.notes && <small>{transaction.notes}</small>}</td><td>{payerLabel(transaction, members)}</td><td className={transaction.direction === "income" ? "positive-text" : "negative-text"}>{transaction.direction === "income" ? "+" : "−"}{formatClp(transaction.amount_clp)}</td><td>{formatUf(transaction.amount_uf, 4)}<small>UF {formatClp(transaction.uf_value)}</small></td><td><button className="icon-button danger" onClick={() => deleteTransaction(transaction.id)} aria-label="Eliminar movimiento"><Trash2 size={14} /></button></td></tr>)}</tbody></table></div>
        ) : <div className="inline-empty"><HandCoins size={24} /><div><strong>Aún no hay movimientos detallados</strong><span>Registra el pie, dividendos, arriendos y gastos indicando quién pagó.</span></div><button className="text-button" onClick={() => openTransaction()}>Agregar el primero</button></div>}
      </section>

      {transactionOpen && <TransactionModal members={members} draft={draft} setDraft={setDraft} splitAmounts={splitAmounts} setSplitAmounts={setSplitAmounts} onAmount={updateAmount} onAllocation={updateAllocation} onRefreshUf={refreshHistoricalUf} onClose={() => setTransactionOpen(false)} onSubmit={saveTransaction} busy={busy} />}
      {inviteOpen && <InviteModal project={project} onClose={() => setInviteOpen(false)} onAdded={() => { setInviteOpen(false); void loadProjectData(); onNotice("Invitación creada. Al iniciar sesión con ese correo verá la inversión."); }} onNotice={onNotice} />}
    </div>
  );
}

function TransactionModal({ members, draft, setDraft, splitAmounts, setSplitAmounts, onAmount, onAllocation, onRefreshUf, onClose, onSubmit, busy }: {
  members: InvestmentMember[];
  draft: TransactionDraft;
  setDraft: React.Dispatch<React.SetStateAction<TransactionDraft>>;
  splitAmounts: Record<string, number>;
  setSplitAmounts: React.Dispatch<React.SetStateAction<Record<string, number>>>;
  onAmount: (amount: number) => void;
  onAllocation: (allocation: string) => void;
  onRefreshUf: () => void;
  onClose: () => void;
  onSubmit: (event: FormEvent) => void;
  busy: boolean;
}) {
  const splitTotal = Object.values(splitAmounts).reduce((sum, value) => sum + number(value), 0);
  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><div className="modal-card compact-modal" role="dialog" aria-modal="true" aria-label="Nuevo movimiento"><div className="modal-header"><div><h2>Nuevo movimiento real</h2><p>Guarda el monto, la UF de la fecha y quién aportó o recibió.</p></div><button className="icon-button" onClick={onClose}><X size={18} /></button></div><form className="modal-form" onSubmit={onSubmit}><div className="form-section form-grid"><label className="field"><span>Fecha</span><input type="date" required value={draft.transaction_date} onChange={(event) => setDraft((current) => ({ ...current, transaction_date: event.target.value }))} onBlur={onRefreshUf} /></label><label className="field"><span>Concepto</span><select value={draft.category} onChange={(event) => setDraft((current) => ({ ...current, category: event.target.value as TransactionCategory }))}>{TRANSACTION_CATEGORIES.map((category) => <option key={category.value} value={category.value}>{category.direction === "income" ? "+ " : "− "}{category.label}</option>)}</select></label><label className="field"><span>Monto total (CLP)</span><input type="number" required min="1" step="1" value={draft.amount_clp || ""} onChange={(event) => onAmount(number(event.target.value))} /></label><label className="field"><span>UF de la fecha</span><div className="inline-control"><input type="number" required min="1" step="0.01" value={draft.uf_value || ""} onChange={(event) => setDraft((current) => ({ ...current, uf_value: number(event.target.value) }))} /><button type="button" className="icon-button" onClick={onRefreshUf} title="Consultar UF"><RefreshCw size={14} /></button></div></label><label className="field wide"><span>¿Quién pagó o recibió?</span><select value={draft.allocation} onChange={(event) => onAllocation(event.target.value)}>{members.map((member) => <option key={member.id} value={member.id}>{member.display_name}</option>)}{members.length > 1 && <option value="shared">Repartido entre varios</option>}</select></label>{draft.allocation === "shared" && <div className="split-editor wide"><div className="split-heading"><span>Distribución exacta</span><strong className={Math.abs(splitTotal - draft.amount_clp) <= 1 ? "positive-text" : "negative-text"}>{formatClp(splitTotal)} / {formatClp(draft.amount_clp)}</strong></div>{members.map((member) => <label key={member.id}><span>{member.display_name} <small>{formatPercent(member.ownership_percentage / 100)}</small></span><input type="number" min="0" step="1" value={splitAmounts[member.id] ?? 0} onChange={(event) => setSplitAmounts((current) => ({ ...current, [member.id]: number(event.target.value) }))} /></label>)}</div>}<label className="field wide"><span>Notas</span><textarea rows={3} value={draft.notes} onChange={(event) => setDraft((current) => ({ ...current, notes: event.target.value }))} placeholder="Ej. cuota 14, reparación de calefón, mes de arriendo…" /></label></div><div className="transaction-preview"><span>Equivalencia histórica</span><strong>{draft.uf_value > 0 ? formatUf(draft.amount_clp / draft.uf_value, 4) : "—"}</strong></div><div className="modal-actions"><button type="button" className="button ghost" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy || !members.length}><Save size={15} /> {busy ? "Guardando…" : "Guardar movimiento"}</button></div></form></div></div>;
}

function InviteModal({ project, onClose, onAdded, onNotice }: { project: Project; onClose: () => void; onAdded: (member: InvestmentMember) => void; onNotice: (message: string) => void }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [ownership, setOwnership] = useState(50);
  const [role, setRole] = useState<"editor" | "viewer">("editor");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const response = await fetch("/api/members", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project_id: project.id, display_name: name, email, ownership_percentage: ownership, role }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error ?? "No fue posible invitar");
      onAdded(payload.member);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No fue posible invitar.");
    } finally {
      setBusy(false);
    }
  }
  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><div className="modal-card invite-modal" role="dialog" aria-modal="true" aria-label="Invitar participante"><div className="modal-header"><div><h2>Compartir inversión</h2><p>El acceso se vincula al correo verificado de su cuenta.</p></div><button className="icon-button" onClick={onClose}><X size={18} /></button></div><form className="modal-form" onSubmit={submit}><div className="form-section form-grid"><label className="field"><span>Nombre</span><input required value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Martín" /></label><label className="field"><span>Correo</span><input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="persona@correo.cl" /></label><label className="field"><span>Participación económica</span><div className="input-suffix"><input type="number" min="0" max="100" step="0.1" value={ownership} onChange={(event) => setOwnership(number(event.target.value))} /><span>%</span></div></label><label className="field"><span>Permiso</span><select value={role} onChange={(event) => setRole(event.target.value as "editor" | "viewer")}><option value="editor">Puede registrar y editar</option><option value="viewer">Sólo lectura</option></select></label></div><p className="modal-help">La invitación no envía correo todavía. Cuando esa persona cree o inicie sesión con este correo, la inversión aparecerá automáticamente.</p><div className="modal-actions"><button type="button" className="button ghost" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy}><UserPlus size={15} /> {busy ? "Compartiendo…" : "Compartir acceso"}</button></div></form></div></div>;
}

function MiniKpi({ icon, label, value, helper }: { icon: React.ReactNode; label: string; value: string; helper: string }) { return <article className="kpi-card neutral"><div className="kpi-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{helper}</small></article>; }
function Metric({ label, value }: { label: string; value: string }) { return <div className="metric-row"><span>{label}</span><strong>{value}</strong></div>; }

function emptyTransaction(project: Project): TransactionDraft {
  return { transaction_date: new Date().toISOString().slice(0, 10), category: "mortgage", amount_clp: 0, uf_value: number(project.uf_value), allocation: "shared", notes: "" };
}

function allocate(amount: number, allocation: string, members: InvestmentMember[]) {
  if (allocation !== "shared") return allocation ? { [allocation]: amount } : {};
  const totalOwnership = members.reduce((sum, member) => sum + number(member.ownership_percentage), 0);
  if (!members.length) return {};
  let assigned = 0;
  return Object.fromEntries(members.map((member, index) => {
    const share = index === members.length - 1
      ? amount - assigned
      : Math.round(amount * (totalOwnership > 0 ? member.ownership_percentage / totalOwnership : 1 / members.length));
    assigned += share;
    return [member.id, share];
  }));
}

function payerLabel(transaction: InvestmentTransaction, members: InvestmentMember[]) {
  const byId = new Map(members.map((member) => [member.id, member.display_name]));
  const splits = transaction.investment_transaction_splits ?? [];
  return splits.map((split) => `${byId.get(split.member_id) ?? "Participante"}: ${formatClp(split.amount_clp, true)}`).join(" · ") || "Sin distribución";
}

function initials(name: string) { return name.split(/\s|@/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join("") || "PI"; }
function formatDate(value: string) { return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value.slice(0, 10)}T12:00:00`)); }
function ivaStatusLabel(status: Project["iva_refund_status"]) { return ({ not_applicable: "no aplica", evaluating: "en evaluación", requested: "solicitada", approved: "aprobada", received: "recibida" })[status] ?? "sin estado"; }
