export type Project = {
  id: string;
  owner_id?: string;
  name: string;
  address: string;
  status: "active" | "planning" | "sold";
  purchase_date: string;
  uf_value: number;
  property_value_uf: number;
  property_value_clp: number;
  down_payment_clp: number;
  mortgage_amount_clp: number;
  annual_mortgage_rate: number;
  mortgage_term_years: number;
  monthly_payment_estimated: number;
  initial_rent_estimated: number;
  rent_growth_annual: number;
  vacancy_rate_estimated: number;
  admin_rate_estimated: number;
  monthly_common_expenses_estimated: number;
  common_expenses_growth_annual: number;
  annual_contributions_estimated: number;
  contributions_growth_annual: number;
  annual_insurance_estimated: number;
  insurance_growth_annual: number;
  maintenance_rate_estimated: number;
  periodic_expense_interval_years: number;
  periodic_expense_clp: number;
  periodic_expense_growth_annual: number;
  annual_appreciation_rate: number;
  closing_cost_rate: number;
  sale_cost_rate: number;
  iva_refund_clp: number;
  planned_sale_year: number;
  notes: string;
  created_at?: string;
  updated_at?: string;
};

export type MonthlyRecord = {
  id: string;
  owner_id?: string;
  project_id: string;
  period: string;
  rent_collected: number;
  mortgage_payment: number;
  vacancy_days: number;
  admin_fee: number;
  common_expenses: number;
  contributions: number;
  insurance: number;
  maintenance: number;
  repairs: number;
  other_expenses: number;
  notes: string;
  created_at?: string;
  updated_at?: string;
};

export type ProjectDraft = Omit<Project, "id" | "owner_id" | "created_at" | "updated_at">;
export type RecordDraft = Omit<MonthlyRecord, "id" | "owner_id" | "created_at" | "updated_at">;

export type MonthlyComparison = {
  period: string;
  label: string;
  estimatedRent: number;
  estimatedExpenses: number;
  estimatedCashflow: number;
  actualRent: number | null;
  actualExpenses: number | null;
  actualCashflow: number | null;
  estimatedDisbursement: number;
  actualDisbursement: number | null;
};

export const EMPTY_PROJECT: ProjectDraft = {
  name: "",
  address: "",
  status: "active",
  purchase_date: new Date().toISOString().slice(0, 10),
  uf_value: 39842,
  property_value_uf: 5000,
  property_value_clp: 199210000,
  down_payment_clp: 39842000,
  mortgage_amount_clp: 159368000,
  annual_mortgage_rate: 0.04,
  mortgage_term_years: 30,
  monthly_payment_estimated: 760000,
  initial_rent_estimated: 1035000,
  rent_growth_annual: 0.04,
  vacancy_rate_estimated: 0.08,
  admin_rate_estimated: 0.08,
  monthly_common_expenses_estimated: 100000,
  common_expenses_growth_annual: 0.03,
  annual_contributions_estimated: 320000,
  contributions_growth_annual: 0.03,
  annual_insurance_estimated: 120000,
  insurance_growth_annual: 0.03,
  maintenance_rate_estimated: 0.005,
  periodic_expense_interval_years: 5,
  periodic_expense_clp: 0,
  periodic_expense_growth_annual: 0.03,
  annual_appreciation_rate: 0.055,
  closing_cost_rate: 0.025,
  sale_cost_rate: 0.025,
  iva_refund_clp: 0,
  planned_sale_year: 10,
  notes: "",
};

export function emptyRecord(projectId: string, period = currentPeriod()): RecordDraft {
  return {
    project_id: projectId,
    period,
    rent_collected: 0,
    mortgage_payment: 0,
    vacancy_days: 0,
    admin_fee: 0,
    common_expenses: 0,
    contributions: 0,
    insurance: 0,
    maintenance: 0,
    repairs: 0,
    other_expenses: 0,
    notes: "",
  };
}

export function currentPeriod() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
}

export function normalizePeriod(value: string) {
  return `${value.slice(0, 7)}-01`;
}

export function recordExpenses(record: MonthlyRecord | RecordDraft) {
  return (
    number(record.mortgage_payment) +
    number(record.admin_fee) +
    number(record.common_expenses) +
    number(record.contributions) +
    number(record.insurance) +
    number(record.maintenance) +
    number(record.repairs) +
    number(record.other_expenses)
  );
}

export function recordCashflow(record: MonthlyRecord | RecordDraft) {
  return number(record.rent_collected) - recordExpenses(record);
}

export function monthlyEstimate(project: Project, period: string) {
  const months = Math.max(0, monthsBetween(project.purchase_date, period));
  const annualFactor = Math.pow(1 + number(project.rent_growth_annual), months / 12);
  const rent = number(project.initial_rent_estimated) * annualFactor;
  const vacancy = rent * number(project.vacancy_rate_estimated);
  const administration = rent * number(project.admin_rate_estimated);
  const valueFactor = Math.pow(1 + number(project.annual_appreciation_rate), months / 12);
  const maintenance =
    (number(project.property_value_clp) * valueFactor * number(project.maintenance_rate_estimated)) / 12;
  const commonExpenses =
    number(project.monthly_common_expenses_estimated) *
    Math.pow(1 + number(project.common_expenses_growth_annual), months / 12);
  const contributions =
    (number(project.annual_contributions_estimated) / 12) *
    Math.pow(1 + number(project.contributions_growth_annual), months / 12);
  const insurance =
    (number(project.annual_insurance_estimated) / 12) *
    Math.pow(1 + number(project.insurance_growth_annual), months / 12);
  const intervalMonths = Math.round(number(project.periodic_expense_interval_years) * 12);
  const occurrence = intervalMonths > 0 && months > 0 && months % intervalMonths === 0
    ? months / intervalMonths
    : 0;
  const extraordinary = occurrence > 0
    ? number(project.periodic_expense_clp) *
      Math.pow(1 + number(project.periodic_expense_growth_annual), months / 12)
    : 0;
  const mortgage = months < number(project.mortgage_term_years) * 12 ? mortgagePayment(project) : 0;
  const expenses =
    mortgage +
    vacancy +
    administration +
    commonExpenses +
    contributions +
    insurance +
    maintenance +
    extraordinary;
  return {
    rent,
    expenses,
    cashflow: rent - expenses,
    mortgage,
    vacancy,
    administration,
    commonExpenses,
    contributions,
    insurance,
    maintenance,
    extraordinary,
  };
}

export function mortgagePayment(project: Project) {
  if (number(project.monthly_payment_estimated) > 0) return number(project.monthly_payment_estimated);
  const principal = number(project.mortgage_amount_clp);
  const months = Math.max(1, number(project.mortgage_term_years) * 12);
  const rate = number(project.annual_mortgage_rate) / 12;
  return rate === 0 ? principal / months : principal * rate / (1 - Math.pow(1 + rate, -months));
}

export function mortgageBalance(project: Project, monthsPaid: number) {
  const principal = number(project.mortgage_amount_clp);
  const totalMonths = Math.max(1, number(project.mortgage_term_years) * 12);
  const paid = Math.min(Math.max(0, monthsPaid), totalMonths);
  const rate = number(project.annual_mortgage_rate) / 12;
  if (paid >= totalMonths) return 0;
  if (rate === 0) return principal * (1 - paid / totalMonths);
  const payment = mortgagePayment(project);
  return Math.max(0, principal * Math.pow(1 + rate, paid) - payment * ((Math.pow(1 + rate, paid) - 1) / rate));
}

export function buildAnnualProjection(project: Project, horizon = 30) {
  let cumulativeCashflow = 0;
  return Array.from({ length: horizon }, (_, index) => {
    const year = index + 1;
    const valueStart = number(project.property_value_clp) * Math.pow(1 + number(project.annual_appreciation_rate), year - 1);
    const valueEnd = number(project.property_value_clp) * Math.pow(1 + number(project.annual_appreciation_rate), year);
    const annualRent = number(project.initial_rent_estimated) * 12 * Math.pow(1 + number(project.rent_growth_annual), year - 1);
    const commonExpenses = number(project.monthly_common_expenses_estimated) * 12 *
      Math.pow(1 + number(project.common_expenses_growth_annual), year - 1);
    const contributions = number(project.annual_contributions_estimated) *
      Math.pow(1 + number(project.contributions_growth_annual), year - 1);
    const insurance = number(project.annual_insurance_estimated) *
      Math.pow(1 + number(project.insurance_growth_annual), year - 1);
    const interval = Math.round(number(project.periodic_expense_interval_years));
    const occurrence = interval > 0 && year % interval === 0 ? year / interval : 0;
    const extraordinary = occurrence > 0
      ? number(project.periodic_expense_clp) *
        Math.pow(1 + number(project.periodic_expense_growth_annual), year)
      : 0;
    const operatingExpenses =
      annualRent * (number(project.vacancy_rate_estimated) + number(project.admin_rate_estimated)) +
      commonExpenses +
      contributions +
      insurance +
      valueStart * number(project.maintenance_rate_estimated) +
      extraordinary;
    const mortgage = year <= number(project.mortgage_term_years) ? mortgagePayment(project) * 12 : 0;
    const cashflow = annualRent - operatingExpenses - mortgage;
    cumulativeCashflow += cashflow;
    const balance = mortgageBalance(project, year * 12);
    const netSale = valueEnd * (1 - number(project.sale_cost_rate)) - balance;
    const netResult =
      netSale + cumulativeCashflow - number(project.down_payment_clp) -
      number(project.property_value_clp) * number(project.closing_cost_rate) + number(project.iva_refund_clp);
    return { year, value: valueEnd, annualRent, operatingExpenses, extraordinary, mortgage, cashflow, cumulativeCashflow, balance, netSale, netResult };
  });
}

export function buildComparisons(project: Project, records: MonthlyRecord[]): MonthlyComparison[] {
  const firstPeriod = normalizePeriod(project.purchase_date);
  const periods = new Set<string>();
  const start = new Date(`${firstPeriod}T12:00:00`);
  const now = new Date();
  const end = new Date(now.getFullYear(), now.getMonth(), 1, 12);
  const maxMonths = Math.min(360, Math.max(1, monthsBetween(firstPeriod, currentPeriod()) + 1));
  for (let index = 0; index < maxMonths; index += 1) {
    const date = new Date(start.getFullYear(), start.getMonth() + index, 1, 12);
    if (date > end) break;
    periods.add(date.toISOString().slice(0, 10));
  }
  records.forEach((record) => periods.add(normalizePeriod(record.period)));
  const byPeriod = new Map(records.map((record) => [normalizePeriod(record.period), record]));

  return [...periods]
    .sort()
    .map((period) => {
      const estimated = monthlyEstimate(project, period);
      const actual = byPeriod.get(period);
      const actualExpenses = actual ? recordExpenses(actual) : null;
      const actualCashflow = actual ? number(actual.rent_collected) - number(actualExpenses) : null;
      return {
        period,
        label: monthLabel(period),
        estimatedRent: estimated.rent,
        estimatedExpenses: estimated.expenses,
        estimatedCashflow: estimated.cashflow,
        actualRent: actual ? number(actual.rent_collected) : null,
        actualExpenses,
        actualCashflow,
        estimatedDisbursement: Math.max(0, -estimated.cashflow),
        actualDisbursement: actualCashflow === null ? null : Math.max(0, -actualCashflow),
      };
    });
}

export function formatClp(value: number | null | undefined, compact = false) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
    notation: compact ? "compact" : "standard",
  }).format(value);
}

export function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("es-CL", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value);
}

export function monthLabel(period: string) {
  const date = new Date(`${normalizePeriod(period)}T12:00:00`);
  return new Intl.DateTimeFormat("es-CL", { month: "short", year: "2-digit" })
    .format(date)
    .replace(" de ", " ");
}

export function number(value: unknown) {
  const parsed = typeof value === "number" ? value : Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function monthsBetween(startValue: string, endValue: string) {
  const start = new Date(`${normalizePeriod(startValue)}T12:00:00`);
  const end = new Date(`${normalizePeriod(endValue)}T12:00:00`);
  return (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth();
}
