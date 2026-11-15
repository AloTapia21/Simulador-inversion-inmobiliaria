"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  BarChart3,
  Building2,
  CalendarDays,
  Check,
  Cloud,
  Database,
  FileDown,
  HardDrive,
  Home,
  Landmark,
  LogOut,
  Menu,
  Pencil,
  Plus,
  ReceiptText,
  Save,
  Settings2,
  TrendingDown,
  TrendingUp,
  WalletCards,
  X,
} from "lucide-react";
import {
  buildAnnualProjection,
  buildComparisons,
  currentPeriod,
  EMPTY_PROJECT,
  emptyRecord,
  formatClp,
  formatPercent,
  monthLabel,
  monthlyEstimate,
  normalizePeriod,
  number,
  recordCashflow,
  recordExpenses,
  type MonthlyRecord,
  type Project,
  type ProjectDraft,
  type RecordDraft,
} from "@/lib/investment";

type StorageMode = "checking" | "cloud" | "local";
type Tab = "summary" | "monthly" | "history" | "projection" | "assumptions";

const PROJECTS_KEY = "inversion-inmobiliaria:projects:v1";
const RECORDS_KEY = "inversion-inmobiliaria:records:v1";

export function InvestmentApp({ displayName, authenticated = false }: { displayName: string; authenticated?: boolean }) {
  const [mode, setMode] = useState<StorageMode>("checking");
  const [projects, setProjects] = useState<Project[]>([]);
  const [recordsByProject, setRecordsByProject] = useState<Record<string, MonthlyRecord[]>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("summary");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [projectDialog, setProjectDialog] = useState(false);
  const [projectDraft, setProjectDraft] = useState<ProjectDraft>({ ...EMPTY_PROJECT });
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [recordDialog, setRecordDialog] = useState(false);
  const [recordDraft, setRecordDraft] = useState<RecordDraft>(emptyRecord(""));
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function initialize() {
    try {
      const status = await fetch("/api/status", { cache: "no-store" }).then((response) => response.json());
      if (status.configured) {
        setMode("cloud");
        const response = await fetch("/api/projects", { cache: "no-store" });
        if (!response.ok) throw new Error("No fue posible cargar Supabase");
        const payload = await response.json();
        setProjects(payload.projects ?? []);
        setSelectedId(payload.projects?.[0]?.id ?? null);
        return;
      }
    } catch (error) {
      console.error(error);
      setNotice("Supabase no respondió; se activó el respaldo local de este navegador.");
    }
    const localProjects = readLocal<Project[]>(PROJECTS_KEY, []);
    const localRecords = readLocal<Record<string, MonthlyRecord[]>>(RECORDS_KEY, {});
    setProjects(localProjects);
    setRecordsByProject(localRecords);
    setSelectedId(localProjects[0]?.id ?? null);
    setMode("local");
  }

  async function loadCloudRecords(projectId: string) {
    const response = await fetch(`/api/records?project_id=${encodeURIComponent(projectId)}`, { cache: "no-store" });
    if (!response.ok) {
      setNotice("No fue posible cargar el historial mensual.");
      return;
    }
    const payload = await response.json();
    setRecordsByProject((current) => ({ ...current, [projectId]: payload.records ?? [] }));
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- client storage/API hydration happens after mount
    void initialize();
  }, []);

  useEffect(() => {
    if (mode !== "cloud" || !selectedId || recordsByProject[selectedId]) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetches records for the selected project
    void loadCloudRecords(selectedId);
  }, [mode, selectedId, recordsByProject]);

  const selected = projects.find((project) => project.id === selectedId) ?? projects[0] ?? null;
  const records = useMemo(
    () => (selected ? recordsByProject[selected.id] ?? [] : []),
    [selected, recordsByProject],
  );
  const comparisons = useMemo(
    () => (selected ? buildComparisons(selected, records) : []),
    [selected, records],
  );
  const projection = useMemo(
    () => (selected ? buildAnnualProjection(selected) : []),
    [selected],
  );

  function openNewProject() {
    setEditingProjectId(null);
    setProjectDraft({ ...EMPTY_PROJECT, purchase_date: new Date().toISOString().slice(0, 10) });
    setProjectDialog(true);
  }

  function openEditProject() {
    if (!selected) return;
    setEditingProjectId(selected.id);
    setProjectDraft(toProjectDraft(selected));
    setProjectDialog(true);
  }

  async function saveProject(event: FormEvent) {
    event.preventDefault();
    if (!projectDraft.name.trim()) return setNotice("Dale un nombre al proyecto.");
    setBusy(true);
    try {
      const normalized = normalizeProject(projectDraft);
      let saved: Project;
      if (mode === "cloud") {
        const response = await fetch(
          editingProjectId ? `/api/projects/${editingProjectId}` : "/api/projects",
          {
            method: editingProjectId ? "PATCH" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(normalized),
          },
        );
        if (!response.ok) throw new Error("No fue posible guardar el proyecto");
        saved = (await response.json()).project;
      } else {
        const existing = projects.find((project) => project.id === editingProjectId);
        saved = {
          ...normalized,
          id: existing?.id ?? crypto.randomUUID(),
          created_at: existing?.created_at ?? new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }
      const next = editingProjectId
        ? projects.map((project) => (project.id === editingProjectId ? saved : project))
        : [saved, ...projects];
      setProjects(next);
      setSelectedId(saved.id);
      if (mode === "local") writeLocal(PROJECTS_KEY, next);
      setProjectDialog(false);
      setNotice(editingProjectId ? "Supuestos actualizados." : "Proyecto creado. Ya puedes registrar su primer mes.");
    } catch (error) {
      console.error(error);
      setNotice("No se pudo guardar. Revisa la conexión y vuelve a intentarlo.");
    } finally {
      setBusy(false);
    }
  }

  function openNewRecord() {
    if (!selected) return;
    setRecordDraft(emptyRecord(selected.id));
    setRecordDialog(true);
  }

  function openExistingRecord(record: MonthlyRecord) {
    setRecordDraft({
      project_id: record.project_id,
      period: normalizePeriod(record.period),
      rent_collected: record.rent_collected,
      mortgage_payment: record.mortgage_payment,
      vacancy_days: record.vacancy_days,
      admin_fee: record.admin_fee,
      common_expenses: record.common_expenses,
      contributions: record.contributions,
      insurance: record.insurance,
      maintenance: record.maintenance,
      repairs: record.repairs,
      other_expenses: record.other_expenses,
      notes: record.notes,
    });
    setRecordDialog(true);
  }

  function prefillEstimate() {
    if (!selected) return;
    const estimate = monthlyEstimate(selected, recordDraft.period);
    setRecordDraft((current) => ({
      ...current,
      rent_collected: Math.round(estimate.rent),
      mortgage_payment: Math.round(estimate.mortgage),
      admin_fee: Math.round(estimate.administration),
      common_expenses: Math.round(estimate.commonExpenses),
      contributions: Math.round(estimate.contributions),
      insurance: Math.round(estimate.insurance),
      maintenance: Math.round(estimate.maintenance),
      repairs: Math.round(estimate.extraordinary),
    }));
  }

  async function saveRecord(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    try {
      const normalized = normalizeRecord({ ...recordDraft, period: normalizePeriod(recordDraft.period) });
      let saved: MonthlyRecord;
      if (mode === "cloud") {
        const response = await fetch("/api/records", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(normalized),
        });
        if (!response.ok) throw new Error("No fue posible guardar el mes");
        saved = (await response.json()).record;
      } else {
        const existing = records.find((record) => normalizePeriod(record.period) === normalized.period);
        saved = {
          ...normalized,
          id: existing?.id ?? crypto.randomUUID(),
          created_at: existing?.created_at ?? new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }
      const nextRecords = [...records.filter((record) => normalizePeriod(record.period) !== saved.period), saved]
        .sort((a, b) => a.period.localeCompare(b.period));
      const nextMap = { ...recordsByProject, [selected.id]: nextRecords };
      setRecordsByProject(nextMap);
      if (mode === "local") writeLocal(RECORDS_KEY, nextMap);
      setRecordDialog(false);
      setNotice(`Registro de ${monthLabel(saved.period)} guardado.`);
    } catch (error) {
      console.error(error);
      setNotice("No se pudo guardar el registro mensual.");
    } finally {
      setBusy(false);
    }
  }

  function exportCsv() {
    if (!selected) return;
    const headers = [
      "Mes", "Arriendo real", "Gastos reales", "Flujo real", "Flujo estimado",
      "Diferencia", "Vacancia días", "Dividendo", "Administración", "Gastos comunes",
      "Contribuciones", "Seguro", "Mantención", "Arreglos", "Otros", "Notas",
    ];
    const rows = records.map((record) => {
      const estimate = monthlyEstimate(selected, record.period);
      const actual = recordCashflow(record);
      return [
        record.period.slice(0, 7), record.rent_collected, recordExpenses(record), actual,
        Math.round(estimate.cashflow), Math.round(actual - estimate.cashflow), record.vacancy_days,
        record.mortgage_payment, record.admin_fee, record.common_expenses, record.contributions,
        record.insurance, record.maintenance, record.repairs, record.other_expenses, record.notes,
      ];
    });
    const csv = [headers, ...rows].map((row) => row.map(csvCell).join(";")).join("\n");
    const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${selected.name.toLowerCase().replace(/[^a-z0-9]+/gi, "-")}-seguimiento.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const actualComparisons = comparisons.filter((item) => item.actualCashflow !== null);
  const cumulativeActual = actualComparisons.reduce((sum, item) => sum + number(item.actualCashflow), 0);
  const cumulativeEstimated = actualComparisons.reduce((sum, item) => sum + item.estimatedCashflow, 0);
  const actualDisbursement = actualComparisons.reduce((sum, item) => sum + number(item.actualDisbursement), 0);
  const expectedDisbursement = actualComparisons.reduce((sum, item) => sum + item.estimatedDisbursement, 0);
  const vacancyDays = records.reduce((sum, record) => sum + number(record.vacancy_days), 0);
  const plannedSale = selected ? projection[Math.max(0, Math.min(29, selected.planned_sale_year - 1))] : null;

  return (
    <div className="app-shell">
      <aside className={`project-sidebar ${sidebarOpen ? "is-open" : ""}`}>
        <div className="brand-block">
          <div className="brand-mark"><Building2 size={19} /></div>
          <div><strong>VETA</strong><span>Control inmobiliario</span></div>
          <button className="icon-button mobile-only" onClick={() => setSidebarOpen(false)} aria-label="Cerrar menú"><X size={18} /></button>
        </div>
        <button className="new-project-button" onClick={openNewProject}><Plus size={17} /> Nuevo proyecto</button>
        <div className="sidebar-label">Tus inversiones</div>
        <nav className="project-list" aria-label="Proyectos inmobiliarios">
          {projects.map((project) => {
            const projectRecords = recordsByProject[project.id] ?? [];
            const last = projectRecords.at(-1);
            return (
              <button
                key={project.id}
                className={`project-item ${project.id === selected?.id ? "active" : ""}`}
                onClick={() => { setSelectedId(project.id); setSidebarOpen(false); }}
              >
                <span className="project-icon"><Home size={16} /></span>
                <span className="project-copy">
                  <strong>{project.name}</strong>
                  <small>{last ? `Actualizado ${monthLabel(last.period)}` : "Sin registros reales"}</small>
                </span>
                <span className={`status-dot ${project.status}`} />
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="storage-card">
            {mode === "cloud" ? <Cloud size={17} /> : mode === "local" ? <HardDrive size={17} /> : <Database size={17} />}
            <div><strong>{mode === "cloud" ? "Supabase activo" : mode === "local" ? "Guardado local" : "Conectando"}</strong><span>{mode === "cloud" ? "Sincronización privada" : "Solo en este navegador"}</span></div>
          </div>
          <div className="user-row">
            <div className="user-chip"><span>{initials(displayName)}</span><div><strong>{displayName}</strong><small>{authenticated ? "Espacio privado" : "Datos en este dispositivo"}</small></div></div>
            {authenticated && <form action="/auth/signout" method="post"><button className="icon-button" aria-label="Cerrar sesión" title="Cerrar sesión"><LogOut size={16} /></button></form>}
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <button className="icon-button mobile-only" onClick={() => setSidebarOpen(true)} aria-label="Abrir menú"><Menu size={20} /></button>
          <div className="breadcrumbs"><span>Portafolio</span><b>/</b><strong>{selected?.name ?? "Nuevo proyecto"}</strong></div>
          <div className="topbar-actions">
            {selected && <button className="button ghost" onClick={exportCsv}><FileDown size={16} /> Exportar</button>}
            {selected && <button className="button primary" onClick={openNewRecord}><Plus size={16} /> Registrar mes</button>}
          </div>
        </header>

        {notice && <div className="notice" role="status"><Check size={16} /><span>{notice}</span><button onClick={() => setNotice(null)}><X size={15} /></button></div>}

        {!selected ? (
          <EmptyState onCreate={openNewProject} mode={mode} />
        ) : (
          <div className="content-wrap">
            <section className="project-heading">
              <div>
                <div className="eyebrow"><span className={`status-pill ${selected.status}`}>{statusLabel(selected.status)}</span><span>Desde {formatDate(selected.purchase_date)}</span></div>
                <h1>{selected.name}</h1>
                <p>{selected.address || "Agrega una dirección para identificar esta propiedad."}</p>
              </div>
              <button className="button ghost" onClick={openEditProject}><Pencil size={15} /> Editar supuestos</button>
            </section>

            <nav className="tabs" aria-label="Vistas del proyecto">
              <TabButton active={tab === "summary"} onClick={() => setTab("summary")} icon={<BarChart3 size={16} />}>Resumen</TabButton>
              <TabButton active={tab === "monthly"} onClick={() => setTab("monthly")} icon={<ReceiptText size={16} />}>Registrar</TabButton>
              <TabButton active={tab === "history"} onClick={() => setTab("history")} icon={<CalendarDays size={16} />}>Historial</TabButton>
              <TabButton active={tab === "projection"} onClick={() => setTab("projection")} icon={<TrendingUp size={16} />}>Proyección</TabButton>
              <TabButton active={tab === "assumptions"} onClick={() => setTab("assumptions")} icon={<Settings2 size={16} />}>Supuestos</TabButton>
            </nav>

            {tab === "summary" && (
              <SummaryView
                project={selected}
                records={records}
                comparisons={comparisons}
                cumulativeActual={cumulativeActual}
                cumulativeEstimated={cumulativeEstimated}
                actualDisbursement={actualDisbursement}
                expectedDisbursement={expectedDisbursement}
                vacancyDays={vacancyDays}
                plannedSale={plannedSale}
                onRegister={openNewRecord}
                onEditRecord={openExistingRecord}
              />
            )}
            {tab === "monthly" && (
              <QuickMonthlyView project={selected} records={records} onRegister={openNewRecord} onEdit={openExistingRecord} />
            )}
            {tab === "history" && (
              <HistoryView project={selected} records={records} onEdit={openExistingRecord} onExport={exportCsv} />
            )}
            {tab === "projection" && <ProjectionView project={selected} projection={projection} />}
            {tab === "assumptions" && <AssumptionsView project={selected} onEdit={openEditProject} />}
          </div>
        )}
      </main>

      {projectDialog && (
        <ProjectDialog draft={projectDraft} setDraft={setProjectDraft} onClose={() => setProjectDialog(false)} onSubmit={saveProject} busy={busy} editing={Boolean(editingProjectId)} />
      )}
      {recordDialog && selected && (
        <RecordDialog project={selected} draft={recordDraft} setDraft={setRecordDraft} onPrefill={prefillEstimate} onClose={() => setRecordDialog(false)} onSubmit={saveRecord} busy={busy} />
      )}
    </div>
  );
}

function SummaryView({
  project, records, comparisons, cumulativeActual, cumulativeEstimated, actualDisbursement,
  expectedDisbursement, vacancyDays, plannedSale, onRegister, onEditRecord,
}: {
  project: Project;
  records: MonthlyRecord[];
  comparisons: ReturnType<typeof buildComparisons>;
  cumulativeActual: number;
  cumulativeEstimated: number;
  actualDisbursement: number;
  expectedDisbursement: number;
  vacancyDays: number;
  plannedSale: ReturnType<typeof buildAnnualProjection>[number] | null;
  onRegister: () => void;
  onEditRecord: (record: MonthlyRecord) => void;
}) {
  const difference = cumulativeActual - cumulativeEstimated;
  const chartData = comparisons.slice(-18).map((item) => ({
    ...item,
    estimated: Math.round(item.estimatedCashflow),
    actual: item.actualCashflow === null ? null : Math.round(item.actualCashflow),
  }));
  const recent = [...records].sort((a, b) => b.period.localeCompare(a.period)).slice(0, 5);
  return (
    <>
      <section className="kpi-grid">
        <KpiCard label="Flujo real acumulado" value={records.length ? formatClp(cumulativeActual, true) : "Sin datos"} helper={`${records.length} meses registrados`} tone={cumulativeActual >= 0 ? "positive" : "negative"} icon={<WalletCards size={18} />} />
        <KpiCard label="Desviación vs estimado" value={records.length ? formatClp(difference, true) : "—"} helper={difference >= 0 ? "Mejor que el plan" : "Bajo la estimación"} tone={difference >= 0 ? "positive" : "negative"} icon={difference >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />} />
        <KpiCard label="Desembolso de bolsillo" value={formatClp(actualDisbursement, true)} helper={`Plan: ${formatClp(expectedDisbursement, true)}`} tone="neutral" icon={<Landmark size={18} />} />
        <KpiCard label="Vacancia acumulada" value={`${vacancyDays} días`} helper={`${formatPercent(vacancyDays / Math.max(1, records.length * 30))} del período`} tone={vacancyDays > 30 ? "negative" : "neutral"} icon={<CalendarDays size={18} />} />
      </section>

      <section className="dashboard-grid">
        <article className="panel chart-panel">
          <div className="panel-heading"><div><span className="panel-kicker">Estimado vs real</span><h2>Flujo de caja mensual</h2></div><span className="chart-unit">CLP</span></div>
          {records.length ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 12, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="actualFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#20d39b" stopOpacity={0.3} /><stop offset="100%" stopColor="#20d39b" stopOpacity={0} /></linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} stroke="#263342" strokeDasharray="3 5" />
                  <XAxis dataKey="label" tick={{ fill: "#8290a3", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={(value) => compactNumber(value)} tick={{ fill: "#8290a3", fontSize: 11 }} axisLine={false} tickLine={false} width={48} />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, color: "#aeb8c7" }} />
                  <Area name="Real" type="monotone" dataKey="actual" stroke="#20d39b" fill="url(#actualFill)" strokeWidth={2.4} connectNulls={false} />
                  <Line name="Estimado" type="monotone" dataKey="estimated" stroke="#ffb84d" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          ) : <ChartEmpty onRegister={onRegister} />}
        </article>

        <article className="panel sale-card">
          <div className="panel-heading"><div><span className="panel-kicker">Escenario de salida</span><h2>Venta año {project.planned_sale_year}</h2></div></div>
          <div className="sale-number"><span>Resultado neto estimado</span><strong>{formatClp(plannedSale?.netResult ?? 0, true)}</strong></div>
          <div className="metric-list">
            <MetricRow label="Valor proyectado" value={formatClp(plannedSale?.value ?? 0, true)} />
            <MetricRow label="Deuda pendiente" value={formatClp(plannedSale?.balance ?? 0, true)} />
            <MetricRow label="Flujo operativo" value={formatClp(plannedSale?.cumulativeCashflow ?? 0, true)} />
            <MetricRow label="Plusvalía anual" value={formatPercent(project.annual_appreciation_rate)} />
          </div>
        </article>
      </section>

      <section className="panel records-panel">
        <div className="panel-heading"><div><span className="panel-kicker">Últimos movimientos</span><h2>Registros mensuales</h2></div><button className="text-button" onClick={onRegister}><Plus size={15} /> Agregar mes</button></div>
        {recent.length ? <RecordsTable project={project} records={recent} onEdit={onEditRecord} compact /> : <InlineEmpty onAction={onRegister} />}
      </section>
    </>
  );
}

function QuickMonthlyView({ project, records, onRegister, onEdit }: { project: Project; records: MonthlyRecord[]; onRegister: () => void; onEdit: (record: MonthlyRecord) => void }) {
  const latest = [...records].sort((a, b) => b.period.localeCompare(a.period))[0];
  const estimate = monthlyEstimate(project, currentPeriod());
  return (
    <section className="monthly-layout">
      <article className="panel action-card">
        <span className="panel-kicker">Cierre del mes</span>
        <h2>{latest ? `Último registro: ${monthLabel(latest.period)}` : "Comienza el seguimiento real"}</h2>
        <p>Anota lo que efectivamente ingresó y salió. El sistema calcula automáticamente la diferencia contra tu plan original.</p>
        <button className="button primary large" onClick={onRegister}><Plus size={18} /> Registrar {monthLabel(currentPeriod())}</button>
        {latest && <button className="button ghost" onClick={() => onEdit(latest)}><Pencil size={15} /> Editar último registro</button>}
      </article>
      <article className="panel estimate-card">
        <span className="panel-kicker">Referencia para este mes</span>
        <h2>Lo que esperaba el modelo</h2>
        <div className="estimate-equation">
          <div><span>Arriendo</span><strong className="positive-text">+{formatClp(estimate.rent)}</strong></div>
          <div><span>Dividendo</span><strong className="negative-text">−{formatClp(estimate.mortgage)}</strong></div>
          <div><span>Vacancia estimada</span><strong className="negative-text">−{formatClp(estimate.vacancy)}</strong></div>
          <div><span>Administración</span><strong className="negative-text">−{formatClp(estimate.administration)}</strong></div>
          <div><span>Gastos comunes</span><strong className="negative-text">−{formatClp(estimate.commonExpenses)}</strong></div>
          <div><span>Contribuciones</span><strong className="negative-text">−{formatClp(estimate.contributions)}</strong></div>
          <div><span>Seguro</span><strong className="negative-text">−{formatClp(estimate.insurance)}</strong></div>
          <div><span>Mantención</span><strong className="negative-text">−{formatClp(estimate.maintenance)}</strong></div>
          {estimate.extraordinary > 0 && <div><span>Gasto extraordinario</span><strong className="negative-text">−{formatClp(estimate.extraordinary)}</strong></div>}
          <div className="estimate-total"><span>Flujo esperado</span><strong>{formatClp(estimate.cashflow)}</strong></div>
        </div>
        <p className="muted-copy">Cada componente se reajusta con sus propios supuestos. El gasto extraordinario aparece sólo en el mes aniversario configurado.</p>
      </article>
    </section>
  );
}

function HistoryView({ project, records, onEdit, onExport }: { project: Project; records: MonthlyRecord[]; onEdit: (record: MonthlyRecord) => void; onExport: () => void }) {
  const ordered = [...records].sort((a, b) => b.period.localeCompare(a.period));
  return (
    <section className="panel records-panel">
      <div className="panel-heading"><div><span className="panel-kicker">Auditoría mensual</span><h2>Historial completo</h2></div><button className="button ghost" onClick={onExport}><FileDown size={15} /> Descargar CSV</button></div>
      {ordered.length ? <RecordsTable project={project} records={ordered} onEdit={onEdit} /> : <InlineEmpty />}
    </section>
  );
}

function ProjectionView({ project, projection }: { project: Project; projection: ReturnType<typeof buildAnnualProjection> }) {
  const selectedYear = projection[Math.max(0, Math.min(29, project.planned_sale_year - 1))];
  return (
    <>
      <section className="projection-hero">
        <div><span className="panel-kicker">Plan financiero</span><h2>Si vendes en el año {project.planned_sale_year}</h2><p>Valor, deuda y operación proyectados con los supuestos guardados.</p></div>
        <div className="projection-result"><span>Resultado neto</span><strong>{formatClp(selectedYear.netResult, true)}</strong></div>
      </section>
      <section className="panel records-panel">
        <div className="table-scroll"><table className="data-table"><thead><tr><th>Año</th><th>Valor depto</th><th>Saldo deuda</th><th>Arriendo anual</th><th>Gastos op.</th><th>Dividendos</th><th>Flujo anual</th><th>Resultado si vende</th></tr></thead><tbody>
          {projection.map((row) => <tr key={row.year} className={row.year === project.planned_sale_year ? "highlight-row" : ""}><td><b>{row.year}</b></td><td>{formatClp(row.value, true)}</td><td>{formatClp(row.balance, true)}</td><td>{formatClp(row.annualRent, true)}</td><td>{formatClp(row.operatingExpenses, true)}</td><td>{formatClp(row.mortgage, true)}</td><td className={row.cashflow >= 0 ? "positive-text" : "negative-text"}>{formatClp(row.cashflow, true)}</td><td><b>{formatClp(row.netResult, true)}</b></td></tr>)}
        </tbody></table></div>
      </section>
    </>
  );
}

function AssumptionsView({ project, onEdit }: { project: Project; onEdit: () => void }) {
  const groups = [
    { title: "Compra y financiamiento", items: [["Valor departamento", `${project.property_value_uf.toLocaleString("es-CL")} UF · ${formatClp(project.property_value_clp)}`], ["Pie", formatClp(project.down_payment_clp)], ["Crédito", formatClp(project.mortgage_amount_clp)], ["Tasa / plazo", `${formatPercent(project.annual_mortgage_rate)} · ${project.mortgage_term_years} años`], ["Dividendo estimado", formatClp(project.monthly_payment_estimated)]] },
    { title: "Operación", items: [["Arriendo inicial", formatClp(project.initial_rent_estimated)], ["Crecimiento arriendo", formatPercent(project.rent_growth_annual)], ["Vacancia", formatPercent(project.vacancy_rate_estimated)], ["Administración", formatPercent(project.admin_rate_estimated)], ["Gastos comunes", `${formatClp(project.monthly_common_expenses_estimated)} · reajuste ${formatPercent(project.common_expenses_growth_annual)}`], ["Contribuciones", `${formatClp(project.annual_contributions_estimated)} · reajuste ${formatPercent(project.contributions_growth_annual)}`], ["Seguro", `${formatClp(project.annual_insurance_estimated)} · reajuste ${formatPercent(project.insurance_growth_annual)}`], ["Mantención", `${formatPercent(project.maintenance_rate_estimated)} del valor/año`], ["Extraordinario", project.periodic_expense_clp > 0 ? `${formatClp(project.periodic_expense_clp)} cada ${project.periodic_expense_interval_years} años` : "Desactivado"]] },
    { title: "Salida", items: [["Plusvalía", formatPercent(project.annual_appreciation_rate)], ["Año de venta", String(project.planned_sale_year)], ["Costo de venta", formatPercent(project.sale_cost_rate)], ["Gastos de cierre", formatPercent(project.closing_cost_rate)], ["Devolución IVA", formatClp(project.iva_refund_clp)]] },
  ];
  return <section className="assumption-grid">{groups.map((group) => <article className="panel assumption-card" key={group.title}><div className="panel-heading"><h2>{group.title}</h2></div>{group.items.map(([label, value]) => <MetricRow key={label} label={label} value={value} />)}</article>)}<button className="button primary assumption-edit" onClick={onEdit}><Pencil size={16} /> Editar todos los supuestos</button></section>;
}

function RecordsTable({ project, records, onEdit, compact = false }: { project: Project; records: MonthlyRecord[]; onEdit: (record: MonthlyRecord) => void; compact?: boolean }) {
  return <div className="table-scroll"><table className="data-table"><thead><tr><th>Mes</th><th>Arriendo</th><th>Gastos</th><th>Flujo real</th><th>Estimado</th><th>Diferencia</th>{!compact && <><th>Vacancia</th><th>Arreglos</th></>}<th></th></tr></thead><tbody>
    {records.map((record) => { const estimate = monthlyEstimate(project, record.period); const actual = recordCashflow(record); const diff = actual - estimate.cashflow; return <tr key={record.id}><td><b>{monthLabel(record.period)}</b></td><td>{formatClp(record.rent_collected, true)}</td><td>{formatClp(recordExpenses(record), true)}</td><td className={actual >= 0 ? "positive-text" : "negative-text"}>{formatClp(actual, true)}</td><td>{formatClp(estimate.cashflow, true)}</td><td className={diff >= 0 ? "positive-text" : "negative-text"}>{diff >= 0 ? "+" : ""}{formatClp(diff, true)}</td>{!compact && <><td>{record.vacancy_days} días</td><td>{formatClp(record.repairs, true)}</td></>}<td><button className="icon-button" onClick={() => onEdit(record)} aria-label={`Editar ${monthLabel(record.period)}`}><Pencil size={15} /></button></td></tr>; })}
  </tbody></table></div>;
}

function ProjectDialog({ draft, setDraft, onClose, onSubmit, busy, editing }: { draft: ProjectDraft; setDraft: (draft: ProjectDraft) => void; onClose: () => void; onSubmit: (event: FormEvent) => void; busy: boolean; editing: boolean }) {
  const set = <K extends keyof ProjectDraft>(key: K, value: ProjectDraft[K]) => setDraft({ ...draft, [key]: value });
  const recalculateValue = (ufValue: number, propertyUf: number) => setDraft({ ...draft, uf_value: ufValue, property_value_uf: propertyUf, property_value_clp: Math.round(ufValue * propertyUf) });
  return <Modal title={editing ? "Editar supuestos" : "Nuevo proyecto inmobiliario"} subtitle="Guarda el escenario base que usarás para comparar cada mes." onClose={onClose}>
    <form onSubmit={onSubmit} className="modal-form">
      <FormSection title="Identificación"><div className="form-grid"><Field label="Nombre del proyecto" wide><input required value={draft.name} onChange={(e) => set("name", e.target.value)} placeholder="Ej. Departamento Ñuñoa" /></Field><Field label="Dirección" wide><input value={draft.address} onChange={(e) => set("address", e.target.value)} placeholder="Calle, comuna" /></Field><Field label="Fecha de compra"><input type="date" value={draft.purchase_date} onChange={(e) => set("purchase_date", e.target.value)} /></Field><Field label="Estado"><select value={draft.status} onChange={(e) => set("status", e.target.value as Project["status"])}><option value="active">En operación</option><option value="planning">En evaluación</option><option value="sold">Vendido</option></select></Field></div></FormSection>
      <FormSection title="Compra y crédito"><div className="form-grid"><MoneyField label="Valor UF" value={draft.uf_value} onChange={(value) => recalculateValue(value, draft.property_value_uf)} /><NumberField label="Valor propiedad (UF)" value={draft.property_value_uf} onChange={(value) => recalculateValue(draft.uf_value, value)} /><MoneyField label="Valor propiedad (CLP)" value={draft.property_value_clp} onChange={(value) => set("property_value_clp", value)} /><MoneyField label="Pie pagado" value={draft.down_payment_clp} onChange={(value) => set("down_payment_clp", value)} /><MoneyField label="Monto crédito" value={draft.mortgage_amount_clp} onChange={(value) => set("mortgage_amount_clp", value)} /><PercentField label="Tasa hipotecaria anual" value={draft.annual_mortgage_rate} onChange={(value) => set("annual_mortgage_rate", value)} /><NumberField label="Plazo crédito (años)" value={draft.mortgage_term_years} onChange={(value) => set("mortgage_term_years", value)} /><MoneyField label="Dividendo mensual estimado" value={draft.monthly_payment_estimated} onChange={(value) => set("monthly_payment_estimated", value)} /></div></FormSection>
      <FormSection title="Operación mensual estimada"><div className="form-grid"><MoneyField label="Arriendo inicial" value={draft.initial_rent_estimated} onChange={(value) => set("initial_rent_estimated", value)} /><PercentField label="Crecimiento anual arriendo" value={draft.rent_growth_annual} onChange={(value) => set("rent_growth_annual", value)} /><PercentField label="Vacancia anual" value={draft.vacancy_rate_estimated} onChange={(value) => set("vacancy_rate_estimated", value)} /><PercentField label="Comisión administradora" value={draft.admin_rate_estimated} onChange={(value) => set("admin_rate_estimated", value)} /><MoneyField label="Gastos comunes mensuales" value={draft.monthly_common_expenses_estimated} onChange={(value) => set("monthly_common_expenses_estimated", value)} /><PercentField label="Reajuste gastos comunes" value={draft.common_expenses_growth_annual} onChange={(value) => set("common_expenses_growth_annual", value)} /><MoneyField label="Contribuciones anuales" value={draft.annual_contributions_estimated} onChange={(value) => set("annual_contributions_estimated", value)} /><PercentField label="Reajuste contribuciones" value={draft.contributions_growth_annual} onChange={(value) => set("contributions_growth_annual", value)} /><MoneyField label="Seguro anual" value={draft.annual_insurance_estimated} onChange={(value) => set("annual_insurance_estimated", value)} /><PercentField label="Reajuste seguro" value={draft.insurance_growth_annual} onChange={(value) => set("insurance_growth_annual", value)} /><PercentField label="Mantención anual / valor" value={draft.maintenance_rate_estimated} onChange={(value) => set("maintenance_rate_estimated", value)} /></div></FormSection>
      <FormSection title="Gasto extraordinario periódico"><div className="form-grid"><MoneyField label="Monto actual por evento (0 lo desactiva)" value={draft.periodic_expense_clp} onChange={(value) => set("periodic_expense_clp", value)} /><NumberField label="Frecuencia (años)" value={draft.periodic_expense_interval_years} onChange={(value) => set("periodic_expense_interval_years", value)} /><PercentField label="Reajuste anual del monto" value={draft.periodic_expense_growth_annual} onChange={(value) => set("periodic_expense_growth_annual", value)} /></div></FormSection>
      <FormSection title="Venta proyectada"><div className="form-grid"><PercentField label="Plusvalía anual" value={draft.annual_appreciation_rate} onChange={(value) => set("annual_appreciation_rate", value)} /><NumberField label="Año planificado de venta" value={draft.planned_sale_year} onChange={(value) => set("planned_sale_year", Math.max(1, Math.min(30, value)))} /><PercentField label="Costo de venta" value={draft.sale_cost_rate} onChange={(value) => set("sale_cost_rate", value)} /><PercentField label="Gastos de cierre" value={draft.closing_cost_rate} onChange={(value) => set("closing_cost_rate", value)} /><MoneyField label="Devolución efectiva IVA" value={draft.iva_refund_clp} onChange={(value) => set("iva_refund_clp", value)} /><Field label="Notas" wide><textarea value={draft.notes} onChange={(e) => set("notes", e.target.value)} rows={3} placeholder="Supuestos, condiciones del crédito, observaciones…" /></Field></div></FormSection>
      <div className="modal-actions"><button type="button" className="button ghost" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy}><Save size={16} /> {busy ? "Guardando…" : editing ? "Guardar cambios" : "Crear proyecto"}</button></div>
    </form>
  </Modal>;
}

function RecordDialog({ project, draft, setDraft, onPrefill, onClose, onSubmit, busy }: { project: Project; draft: RecordDraft; setDraft: (draft: RecordDraft) => void; onPrefill: () => void; onClose: () => void; onSubmit: (event: FormEvent) => void; busy: boolean }) {
  const set = <K extends keyof RecordDraft>(key: K, value: RecordDraft[K]) => setDraft({ ...draft, [key]: value });
  const estimate = monthlyEstimate(project, draft.period);
  const actual = recordCashflow(draft);
  const difference = actual - estimate.cashflow;
  return <Modal title="Registrar resultado mensual" subtitle={`${project.name} · compara caja real contra el plan.`} onClose={onClose}>
    <form onSubmit={onSubmit} className="modal-form">
      <div className="record-toolbar"><Field label="Mes"><input type="month" required value={draft.period.slice(0, 7)} onChange={(e) => set("period", `${e.target.value}-01`)} /></Field><button type="button" className="button ghost" onClick={onPrefill}>Usar valores estimados</button></div>
      <FormSection title="Ingresos y financiamiento"><div className="form-grid"><MoneyField label="Arriendo efectivamente cobrado" value={draft.rent_collected} onChange={(value) => set("rent_collected", value)} /><MoneyField label="Dividendo pagado" value={draft.mortgage_payment} onChange={(value) => set("mortgage_payment", value)} /><NumberField label="Días de vacancia" value={draft.vacancy_days} onChange={(value) => set("vacancy_days", Math.max(0, Math.min(31, value)))} /></div></FormSection>
      <FormSection title="Desembolsos reales"><div className="form-grid"><MoneyField label="Comisión administradora" value={draft.admin_fee} onChange={(value) => set("admin_fee", value)} /><MoneyField label="Gastos comunes" value={draft.common_expenses} onChange={(value) => set("common_expenses", value)} /><MoneyField label="Contribuciones" value={draft.contributions} onChange={(value) => set("contributions", value)} /><MoneyField label="Seguro" value={draft.insurance} onChange={(value) => set("insurance", value)} /><MoneyField label="Mantención" value={draft.maintenance} onChange={(value) => set("maintenance", value)} /><MoneyField label="Arreglos / reparaciones" value={draft.repairs} onChange={(value) => set("repairs", value)} /><MoneyField label="Otros desembolsos" value={draft.other_expenses} onChange={(value) => set("other_expenses", value)} /><Field label="Notas del mes" wide><textarea rows={3} value={draft.notes} onChange={(e) => set("notes", e.target.value)} placeholder="Qué ocurrió este mes, detalle de arreglos, cobros extraordinarios…" /></Field></div></FormSection>
      <div className="record-preview"><div><span>Flujo estimado</span><strong>{formatClp(estimate.cashflow)}</strong></div><div><span>Flujo real</span><strong className={actual >= 0 ? "positive-text" : "negative-text"}>{formatClp(actual)}</strong></div><div><span>Diferencia</span><strong className={difference >= 0 ? "positive-text" : "negative-text"}>{difference >= 0 ? "+" : ""}{formatClp(difference)}</strong></div><div className="record-disbursement"><span>Aporte de bolsillo</span><strong>{formatClp(Math.max(0, -actual))}</strong></div></div>
      <div className="modal-actions"><button type="button" className="button ghost" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy}><Save size={16} /> {busy ? "Guardando…" : "Guardar mes"}</button></div>
    </form>
  </Modal>;
}

function EmptyState({ onCreate, mode }: { onCreate: () => void; mode: StorageMode }) { return <section className="empty-workspace"><div className="empty-illustration"><Building2 size={34} /></div><span className="panel-kicker">Tu portafolio empieza aquí</span><h1>Crea tu primera inversión</h1><p>Guarda el escenario estimado y, mes a mes, compara arriendo, dividendo, vacancia, arreglos y cada peso que sale de tu bolsillo.</p><button className="button primary large" onClick={onCreate}><Plus size={18} /> Crear proyecto</button><small>{mode === "cloud" ? "Se guardará de forma privada en Supabase." : "Se guardará localmente hasta conectar Supabase."}</small></section>; }
function Modal({ title, subtitle, onClose, children }: { title: string; subtitle: string; onClose: () => void; children: React.ReactNode }) { return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><div className="modal-card" role="dialog" aria-modal="true" aria-label={title}><div className="modal-header"><div><h2>{title}</h2><p>{subtitle}</p></div><button className="icon-button" onClick={onClose} aria-label="Cerrar"><X size={18} /></button></div>{children}</div></div>; }
function FormSection({ title, children }: { title: string; children: React.ReactNode }) { return <section className="form-section"><h3>{title}</h3>{children}</section>; }
function Field({ label, wide = false, children }: { label: string; wide?: boolean; children: React.ReactNode }) { return <label className={`field ${wide ? "wide" : ""}`}><span>{label}</span>{children}</label>; }
function MoneyField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) { return <Field label={label}><div className="input-prefix"><span>$</span><input type="number" min="0" step="1000" value={value} onChange={(e) => onChange(number(e.target.value))} /></div></Field>; }
function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) { return <Field label={label}><input type="number" min="0" step="1" value={value} onChange={(e) => onChange(number(e.target.value))} /></Field>; }
function PercentField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) { return <Field label={label}><div className="input-suffix"><input type="number" min="0" step="0.1" value={Math.round(value * 10000) / 100} onChange={(e) => onChange(number(e.target.value) / 100)} /><span>%</span></div></Field>; }
function TabButton({ active, onClick, icon, children }: { active: boolean; onClick: () => void; icon: React.ReactNode; children: React.ReactNode }) { return <button className={active ? "active" : ""} onClick={onClick}>{icon}{children}</button>; }
function KpiCard({ label, value, helper, tone, icon }: { label: string; value: string; helper: string; tone: "positive" | "negative" | "neutral"; icon: React.ReactNode }) { return <article className={`kpi-card ${tone}`}><div className="kpi-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{helper}</small></article>; }
function MetricRow({ label, value }: { label: string; value: string }) { return <div className="metric-row"><span>{label}</span><strong>{value}</strong></div>; }
function ChartEmpty({ onRegister }: { onRegister: () => void }) { return <div className="chart-empty"><BarChart3 size={28} /><strong>Aún no hay meses reales</strong><span>Registra un mes para iniciar la comparación.</span><button className="text-button" onClick={onRegister}>Registrar ahora</button></div>; }
function InlineEmpty({ onAction }: { onAction?: () => void }) { return <div className="inline-empty"><ReceiptText size={24} /><div><strong>Sin registros mensuales</strong><span>Cuando cierres un mes aparecerá aquí.</span></div>{onAction && <button className="text-button" onClick={onAction}>Agregar mes</button>}</div>; }
function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) { if (!active || !payload?.length) return null; return <div className="chart-tooltip"><b>{label}</b>{payload.map((item) => <div key={item.name}><span style={{ background: item.color }} />{item.name}<strong>{formatClp(item.value, true)}</strong></div>)}</div>; }

function normalizeProject(draft: ProjectDraft): ProjectDraft { const numericKeys: Array<keyof ProjectDraft> = ["uf_value", "property_value_uf", "property_value_clp", "down_payment_clp", "mortgage_amount_clp", "annual_mortgage_rate", "mortgage_term_years", "monthly_payment_estimated", "initial_rent_estimated", "rent_growth_annual", "vacancy_rate_estimated", "admin_rate_estimated", "monthly_common_expenses_estimated", "common_expenses_growth_annual", "annual_contributions_estimated", "contributions_growth_annual", "annual_insurance_estimated", "insurance_growth_annual", "maintenance_rate_estimated", "periodic_expense_interval_years", "periodic_expense_clp", "periodic_expense_growth_annual", "annual_appreciation_rate", "closing_cost_rate", "sale_cost_rate", "iva_refund_clp", "planned_sale_year"]; const result = { ...draft }; numericKeys.forEach((key) => { (result as Record<string, unknown>)[key] = number(result[key]); }); return result; }
function normalizeRecord(draft: RecordDraft): RecordDraft { const numericKeys: Array<keyof RecordDraft> = ["rent_collected", "mortgage_payment", "vacancy_days", "admin_fee", "common_expenses", "contributions", "insurance", "maintenance", "repairs", "other_expenses"]; const result = { ...draft, period: normalizePeriod(draft.period) }; numericKeys.forEach((key) => { (result as Record<string, unknown>)[key] = number(result[key]); }); return result; }
function toProjectDraft(project: Project): ProjectDraft { const draft = { ...project } as Record<string, unknown>; ["id", "owner_id", "created_at", "updated_at"].forEach((key) => delete draft[key]); return { ...EMPTY_PROJECT, ...draft } as ProjectDraft; }
function readLocal<T>(key: string, fallback: T): T { try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) as T : fallback; } catch { return fallback; } }
function writeLocal(key: string, value: unknown) { localStorage.setItem(key, JSON.stringify(value)); }
function csvCell(value: unknown) { const text = String(value ?? ""); return /[;"\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text; }
function initials(name: string) { return name.split(/\s|@/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join("") || "AT"; }
function statusLabel(status: Project["status"]) { return status === "active" ? "En operación" : status === "planning" ? "En evaluación" : "Vendido"; }
function formatDate(value: string) { return new Intl.DateTimeFormat("es-CL", { month: "short", year: "numeric" }).format(new Date(`${value}T12:00:00`)); }
function compactNumber(value: number) { return new Intl.NumberFormat("es-CL", { notation: "compact", maximumFractionDigits: 1 }).format(value); }
