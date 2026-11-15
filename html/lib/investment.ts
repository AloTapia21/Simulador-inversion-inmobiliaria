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
  current_market_value_uf: number;
  down_payment_clp: number;
  down_payment_bonus_clp: number;
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
  iva_refund_status: "not_applicable" | "evaluating" | "requested" | "approved" | "received";
  iva_refund_expected_date: string | null;
  dfl2_qualified: boolean;
  property_surface_m2: number;
  property_is_new: boolean;
  acquisition_owner_type: "natural_person" | "individual_business" | "company";
  dfl2_property_number: number;
  estimated_income_tax_rate: number;
  use_dfl2_5pct_regime: boolean;
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

export type InvestmentMember = {
  id: string;
  project_id: string;
  user_id?: string | null;
  invited_email?: string | null;
  display_name: string;
  role: "owner" | "editor" | "viewer";
  ownership_percentage: number;
  created_at?: string;
  updated_at?: string;
};

export type TransactionCategory =
  | "rent"
  | "iva_refund"
  | "other_income"
  | "down_payment"
  | "closing_costs"
  | "mortgage"
  | "administration"
  | "common_expenses"
  | "contributions"
  | "income_tax"
  | "insurance"
  | "maintenance"
  | "repairs"
  | "furnishing"
  | "other_expense";

export type TransactionSplit = {
  id?: string;
  project_id: string;
  transaction_id?: string;
  member_id: string;
  amount_clp: number;
  amount_uf: number;
};

export type InvestmentTransaction = {
  id: string;
  project_id: string;
  transaction_date: string;
  category: TransactionCategory;
  direction: "income" | "expense";
  amount_clp: number;
  uf_value: number;
  amount_uf: number;
  notes: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  investment_transaction_splits?: TransactionSplit[];
};

export const TRANSACTION_CATEGORIES: Array<{
  value: TransactionCategory;
  label: string;
  direction: "income" | "expense";
  operating: boolean;
}> = [
  { value: "rent", label: "Arriendo recibido", direction: "income", operating: true },
  { value: "iva_refund", label: "Devolución de IVA", direction: "income", operating: false },
  { value: "other_income", label: "Otro ingreso", direction: "income", operating: true },
  { value: "down_payment", label: "Pie", direction: "expense", operating: false },
  { value: "closing_costs", label: "Gastos de compra / cierre", direction: "expense", operating: false },
  { value: "mortgage", label: "Dividendo", direction: "expense", operating: true },
  { value: "administration", label: "Comisión administradora", direction: "expense", operating: true },
  { value: "common_expenses", label: "Gastos comunes", direction: "expense", operating: true },
  { value: "contributions", label: "Contribuciones", direction: "expense", operating: true },
  { value: "income_tax", label: "Impuesto a la renta del arriendo", direction: "expense", operating: true },
  { value: "insurance", label: "Seguro", direction: "expense", operating: true },
  { value: "maintenance", label: "Mantención", direction: "expense", operating: true },
  { value: "repairs", label: "Arreglos / reparaciones", direction: "expense", operating: true },
  { value: "furnishing", label: "Muebles / equipamiento", direction: "expense", operating: false },
  { value: "other_expense", label: "Otro desembolso", direction: "expense", operating: true },
];

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
  current_market_value_uf: 0,
  down_payment_clp: 39842000,
  down_payment_bonus_clp: 0,
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
  iva_refund_status: "not_applicable",
  iva_refund_expected_date: null,
  dfl2_qualified: false,
  property_surface_m2: 0,
  property_is_new: true,
  acquisition_owner_type: "natural_person",
  dfl2_property_number: 1,
  estimated_income_tax_rate: 0,
  use_dfl2_5pct_regime: false,
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
  const incomeTax = rent * rentalIncomeTaxRate(project, period);
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
    incomeTax +
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
    incomeTax,
    extraordinary,
  };
}

export function plannedAcquisitionSummary(project: Project) {
  const contractualDownPayment = number(project.down_payment_clp);
  const downPaymentBonus = Math.min(contractualDownPayment, number(project.down_payment_bonus_clp));
  const cashDownPayment = Math.max(0, contractualDownPayment - downPaymentBonus);
  const closingCosts = number(project.property_value_clp) * number(project.closing_cost_rate);
  const cashRequiredAtPurchase = cashDownPayment + closingCosts;
  const expectedVatRefund = project.iva_refund_status === "not_applicable" ? 0 : number(project.iva_refund_clp);
  const netCapitalAfterRefund = cashRequiredAtPurchase - expectedVatRefund;
  return {
    contractualDownPayment,
    downPaymentBonus,
    cashDownPayment,
    closingCosts,
    cashRequiredAtPurchase,
    expectedVatRefund,
    netCapitalAfterRefund,
  };
}

export function dfl2Assessment(project: Project, date = new Date().toISOString().slice(0, 10)) {
  const assessmentDate = date.length === 7 ? `${date}-01` : date.slice(0, 10);
  const qualifiesAsHousing = Boolean(project.dfl2_qualified) &&
    number(project.property_surface_m2) > 0 &&
    number(project.property_surface_m2) <= 140;
  const naturalPerson = project.acquisition_owner_type === "natural_person";
  const withinFirstTwo = number(project.dfl2_property_number) > 0 && number(project.dfl2_property_number) <= 2;
  const currentlyExempt = qualifiesAsHousing && naturalPerson && withinFirstTwo;
  const purchase = project.purchase_date;
  const transitionalNewHousing = Boolean(project.property_is_new) &&
    number(project.property_surface_m2) <= 140 &&
    purchase >= "2026-10-17" && purchase <= "2027-10-17";
  const specialRegimeEligible = qualifiesAsHousing &&
    (number(project.property_surface_m2) <= 90 || transitionalNewHousing);
  const specialRegimeActive = assessmentDate >= "2027-01-01" &&
    Boolean(project.use_dfl2_5pct_regime) &&
    specialRegimeEligible &&
    !currentlyExempt;
  return {
    qualifiesAsHousing,
    naturalPerson,
    withinFirstTwo,
    currentlyExempt,
    specialRegimeEligible,
    specialRegimeActive,
    effectiveTaxRate: currentlyExempt ? 0 : specialRegimeActive ? 0.05 : number(project.estimated_income_tax_rate),
  };
}

export function rentalIncomeTaxRate(project: Project, date: string) {
  return dfl2Assessment(project, date).effectiveTaxRate;
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

export function mortgageSchedule(project: Project, monthsPaid: number) {
  const limit = Math.min(
    Math.max(0, Math.floor(monthsPaid)),
    Math.max(1, number(project.mortgage_term_years) * 12),
  );
  const payment = mortgagePayment(project);
  const monthlyRate = number(project.annual_mortgage_rate) / 12;
  let balance = number(project.mortgage_amount_clp);
  let interestPaid = 0;
  let principalPaid = 0;
  for (let month = 0; month < limit && balance > 0; month += 1) {
    const interest = balance * monthlyRate;
    const principal = Math.min(balance, Math.max(0, payment - interest));
    interestPaid += interest;
    principalPaid += principal;
    balance -= principal;
  }
  return { payment, balance: Math.max(0, balance), interestPaid, principalPaid, payments: limit };
}

export function currentInvestmentSnapshot(
  project: Project,
  transactions: InvestmentTransaction[],
  currentUf: number,
  valuationDate = new Date().toISOString().slice(0, 10),
) {
  const elapsedMonths = Math.max(0, monthsBetween(project.purchase_date, valuationDate));
  const years = elapsedMonths / 12;
  const engineValueUf = number(project.property_value_uf) *
    Math.pow(1 + number(project.annual_appreciation_rate), years);
  const marketValueUf = number(project.current_market_value_uf) > 0
    ? number(project.current_market_value_uf)
    : engineValueUf;
  const marketValueClp = marketValueUf * number(currentUf);
  const ufIndexedPurchaseValueClp = number(project.property_value_uf) * number(currentUf);
  const schedule = mortgageSchedule(project, elapsedMonths);
  const mortgagePaid = sumTransactions(transactions, "mortgage", "expense");
  const rentCollected = sumTransactions(transactions, "rent", "income");
  const totalIncome = transactions
    .filter((item) => item.direction === "income")
    .reduce((sum, item) => sum + number(item.amount_clp), 0);
  const totalExpenses = transactions
    .filter((item) => item.direction === "expense")
    .reduce((sum, item) => sum + number(item.amount_clp), 0);
  const operatingCashflow = transactions
    .filter((item) => TRANSACTION_CATEGORIES.find((category) => category.value === item.category)?.operating)
    .reduce((sum, item) => sum + (item.direction === "income" ? 1 : -1) * number(item.amount_clp), 0);
  const equity = marketValueClp - schedule.balance;
  const actualIrr = calculateXirr([
    ...transactions.map((item) => ({
      date: item.transaction_date,
      amount: (item.direction === "income" ? 1 : -1) * number(item.amount_clp),
    })),
    { date: valuationDate, amount: Math.max(0, equity) },
  ]);
  return {
    elapsedMonths,
    engineValueUf,
    marketValueUf,
    marketValueClp,
    ufIndexedPurchaseValueClp,
    mortgageBalance: schedule.balance,
    scheduledPrincipalPaid: schedule.principalPaid,
    scheduledInterestPaid: schedule.interestPaid,
    scheduledMortgagePaid: schedule.payment * schedule.payments,
    mortgagePaid,
    rentCollected,
    totalIncome,
    totalExpenses,
    operatingCashflow,
    equity,
    actualIrr,
  };
}

export function memberContributionSummary(
  members: InvestmentMember[],
  transactions: InvestmentTransaction[],
  currentUf: number,
) {
  return members.map((member) => {
    const splits = transactions.flatMap((transaction) =>
      (transaction.investment_transaction_splits ?? [])
        .filter((split) => split.member_id === member.id)
        .map((split) => ({ transaction, split })),
    );
    const expensesClp = splits
      .filter(({ transaction }) => transaction.direction === "expense")
      .reduce((sum, { split }) => sum + number(split.amount_clp), 0);
    const incomeClp = splits
      .filter(({ transaction }) => transaction.direction === "income")
      .reduce((sum, { split }) => sum + number(split.amount_clp), 0);
    const expensesUf = splits
      .filter(({ transaction }) => transaction.direction === "expense")
      .reduce((sum, { split }) => sum + number(split.amount_uf), 0);
    const incomeUf = splits
      .filter(({ transaction }) => transaction.direction === "income")
      .reduce((sum, { split }) => sum + number(split.amount_uf), 0);
    return {
      member,
      expensesClp,
      incomeClp,
      netContributionClp: expensesClp - incomeClp,
      netContributionUf: expensesUf - incomeUf,
      currentEquivalentClp: (expensesUf - incomeUf) * number(currentUf),
    };
  });
}

export function calculateXirr(flows: Array<{ date: string; amount: number }>) {
  const valid = flows
    .filter((flow) => Number.isFinite(flow.amount) && flow.amount !== 0 && /^\d{4}-\d{2}-\d{2}/.test(flow.date))
    .sort((a, b) => a.date.localeCompare(b.date));
  if (!valid.some((flow) => flow.amount < 0) || !valid.some((flow) => flow.amount > 0)) return null;
  const start = new Date(`${valid[0].date.slice(0, 10)}T12:00:00`).getTime();
  const npv = (rate: number) => valid.reduce((sum, flow) => {
    const date = new Date(`${flow.date.slice(0, 10)}T12:00:00`).getTime();
    const years = (date - start) / (365.25 * 24 * 60 * 60 * 1000);
    return sum + flow.amount / Math.pow(1 + rate, years);
  }, 0);
  let low = -0.9999;
  let high = 10;
  let lowValue = npv(low);
  let highValue = npv(high);
  if (lowValue * highValue > 0) return null;
  for (let iteration = 0; iteration < 160; iteration += 1) {
    const middle = (low + high) / 2;
    const middleValue = npv(middle);
    if (Math.abs(middleValue) < 0.01) return middle;
    if (lowValue * middleValue <= 0) {
      high = middle;
      highValue = middleValue;
    } else {
      low = middle;
      lowValue = middleValue;
    }
  }
  return (low + high) / 2;
}

export function formatUf(value: number | null | undefined, maximumFractionDigits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${new Intl.NumberFormat("es-CL", { maximumFractionDigits }).format(value)} UF`;
}

export function transactionCategory(category: TransactionCategory) {
  return TRANSACTION_CATEGORIES.find((item) => item.value === category) ?? TRANSACTION_CATEGORIES.at(-1)!;
}

function sumTransactions(
  transactions: InvestmentTransaction[],
  category: TransactionCategory,
  direction: "income" | "expense",
) {
  return transactions
    .filter((item) => item.category === category && item.direction === direction)
    .reduce((sum, item) => sum + number(item.amount_clp), 0);
}

export function buildAnnualProjection(project: Project, horizon = 30) {
  let cumulativeCashflow = 0;
  const purchaseDate = new Date(`${project.purchase_date}T12:00:00`);
  const acquisition = plannedAcquisitionSummary(project);
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
    const projectionDate = new Date(purchaseDate.getFullYear() + year, purchaseDate.getMonth(), purchaseDate.getDate(), 12)
      .toISOString().slice(0, 10);
    const incomeTax = annualRent * rentalIncomeTaxRate(project, projectionDate);
    const operatingExpenses =
      annualRent * (number(project.vacancy_rate_estimated) + number(project.admin_rate_estimated)) +
      commonExpenses +
      contributions +
      insurance +
      valueStart * number(project.maintenance_rate_estimated) +
      incomeTax +
      extraordinary;
    const mortgage = year <= number(project.mortgage_term_years) ? mortgagePayment(project) * 12 : 0;
    const balanceStart = mortgageBalance(project, (year - 1) * 12);
    const balance = mortgageBalance(project, year * 12);
    const principalPaid = Math.max(0, balanceStart - balance);
    const interestPaid = Math.max(0, mortgage - principalPaid);
    const cashflow = annualRent - operatingExpenses - mortgage;
    cumulativeCashflow += cashflow;
    const netSale = valueEnd * (1 - number(project.sale_cost_rate)) - balance;
    const netResult =
      netSale + cumulativeCashflow - acquisition.cashRequiredAtPurchase + acquisition.expectedVatRefund;
    return { year, value: valueEnd, annualRent, operatingExpenses, incomeTax, extraordinary, mortgage, principalPaid, interestPaid, cashflow, cumulativeCashflow, balance, netSale, netResult };
  });
}

export function projectedInvestmentIrr(project: Project, saleYear = project.planned_sale_year) {
  const projection = buildAnnualProjection(project, Math.max(1, saleYear));
  const purchase = new Date(`${project.purchase_date}T12:00:00`);
  const acquisition = plannedAcquisitionSummary(project);
  const flows: Array<{ date: string; amount: number }> = [
    { date: project.purchase_date, amount: -acquisition.cashRequiredAtPurchase },
  ];
  if (acquisition.expectedVatRefund > 0) {
    flows.push({
      date: project.iva_refund_expected_date || addMonths(project.purchase_date, 6),
      amount: acquisition.expectedVatRefund,
    });
  }
  projection.slice(0, saleYear).forEach((row) => {
    const date = new Date(purchase.getFullYear() + row.year, purchase.getMonth(), purchase.getDate(), 12);
    const amount = row.cashflow + (row.year === saleYear ? row.netSale : 0);
    flows.push({ date: date.toISOString().slice(0, 10), amount });
  });
  return calculateXirr(flows);
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

function addMonths(value: string, months: number) {
  const date = new Date(`${value.slice(0, 10)}T12:00:00`);
  date.setMonth(date.getMonth() + months);
  return date.toISOString().slice(0, 10);
}
