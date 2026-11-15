import { NextResponse } from "next/server";
import { normalizePeriod, type MonthlyRecord, type Project } from "./investment";

export function sanitizeProject(body: Record<string, unknown>) {
  const allowed = [
    "name", "address", "status", "purchase_date", "uf_value", "property_value_uf",
    "property_value_clp", "down_payment_clp", "mortgage_amount_clp", "annual_mortgage_rate",
    "mortgage_term_years", "monthly_payment_estimated", "initial_rent_estimated",
    "rent_growth_annual", "vacancy_rate_estimated", "admin_rate_estimated",
    "monthly_common_expenses_estimated", "common_expenses_growth_annual",
    "annual_contributions_estimated", "contributions_growth_annual",
    "annual_insurance_estimated", "insurance_growth_annual", "maintenance_rate_estimated",
    "periodic_expense_interval_years", "periodic_expense_clp", "periodic_expense_growth_annual",
    "annual_appreciation_rate",
    "closing_cost_rate", "sale_cost_rate", "iva_refund_clp", "planned_sale_year", "notes",
  ];
  return Object.fromEntries(allowed.filter((key) => key in body).map((key) => [key, body[key]]));
}

export function coerceProject(project: Project) {
  const numeric = [
    "uf_value", "property_value_uf", "property_value_clp", "down_payment_clp",
    "mortgage_amount_clp", "annual_mortgage_rate", "mortgage_term_years",
    "monthly_payment_estimated", "initial_rent_estimated", "rent_growth_annual",
    "vacancy_rate_estimated", "admin_rate_estimated", "monthly_common_expenses_estimated",
    "common_expenses_growth_annual", "annual_contributions_estimated", "contributions_growth_annual",
    "annual_insurance_estimated", "insurance_growth_annual", "maintenance_rate_estimated",
    "periodic_expense_interval_years", "periodic_expense_clp", "periodic_expense_growth_annual",
    "annual_appreciation_rate", "closing_cost_rate", "sale_cost_rate", "iva_refund_clp",
    "planned_sale_year",
  ];
  const result = { ...project } as Project & Record<string, unknown>;
  numeric.forEach((key) => { result[key] = Number(result[key] ?? 0); });
  return result as Project;
}

export function sanitizeRecord(body: Record<string, unknown>) {
  const numeric = [
    "rent_collected", "mortgage_payment", "vacancy_days", "admin_fee", "common_expenses",
    "contributions", "insurance", "maintenance", "repairs", "other_expenses",
  ];
  return {
    project_id: String(body.project_id ?? ""),
    period: normalizePeriod(String(body.period ?? "")),
    ...Object.fromEntries(numeric.map((key) => [key, Number(body[key] ?? 0)])),
    notes: String(body.notes ?? ""),
  };
}

export function coerceRecord(record: MonthlyRecord) {
  const numeric = [
    "rent_collected", "mortgage_payment", "vacancy_days", "admin_fee", "common_expenses",
    "contributions", "insurance", "maintenance", "repairs", "other_expenses",
  ];
  const result = { ...record } as MonthlyRecord & Record<string, unknown>;
  numeric.forEach((key) => { result[key] = Number(result[key] ?? 0); });
  return result as MonthlyRecord;
}

export function apiError(error: unknown) {
  console.error(error);
  return NextResponse.json({ error: "No fue posible acceder a la base de datos" }, { status: 500 });
}
