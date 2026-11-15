import assert from "node:assert/strict";
import test from "node:test";
import {
  EMPTY_PROJECT,
  calculateXirr,
  currentInvestmentSnapshot,
  dfl2Assessment,
  memberContributionSummary,
  mortgageBalance,
  plannedAcquisitionSummary,
  projectedInvestmentIrr,
} from "../lib/investment.ts";

function project(overrides = {}) {
  return {
    ...EMPTY_PROJECT,
    ...overrides,
    id: "project-1",
    purchase_date: "2025-01-01",
  };
}

test("mortgage balance falls after payments", () => {
  const investment = project({ monthly_payment_estimated: 0 });
  assert.ok(mortgageBalance(investment, 12) < investment.mortgage_amount_clp);
  assert.equal(mortgageBalance(investment, investment.mortgage_term_years * 12), 0);
});

test("current value uses current UF and real appreciation", () => {
  const investment = project({ property_value_uf: 5000, annual_appreciation_rate: 0, current_market_value_uf: 0 });
  const snapshot = currentInvestmentSnapshot(investment, [], 41_000, "2026-01-01");
  assert.equal(snapshot.marketValueUf, 5000);
  assert.equal(snapshot.marketValueClp, 205_000_000);
});

test("manual market value overrides engine valuation", () => {
  const investment = project({ property_value_uf: 5000, current_market_value_uf: 5400 });
  const snapshot = currentInvestmentSnapshot(investment, [], 40_000, "2026-01-01");
  assert.equal(snapshot.marketValueClp, 216_000_000);
});

test("member contributions preserve exact transaction splits", () => {
  const members = [
    { id: "a", project_id: "project-1", display_name: "A", role: "owner", ownership_percentage: 50 },
    { id: "b", project_id: "project-1", display_name: "B", role: "editor", ownership_percentage: 50 },
  ];
  const transactions = [{
    id: "tx", project_id: "project-1", transaction_date: "2025-01-01", category: "down_payment",
    direction: "expense", amount_clp: 1_000_000, uf_value: 40_000, amount_uf: 25, notes: "",
    investment_transaction_splits: [
      { project_id: "project-1", member_id: "a", amount_clp: 700_000, amount_uf: 17.5 },
      { project_id: "project-1", member_id: "b", amount_clp: 300_000, amount_uf: 7.5 },
    ],
  }];
  const summary = memberContributionSummary(members, transactions, 42_000);
  assert.equal(summary[0].netContributionClp, 700_000);
  assert.equal(summary[1].currentEquivalentClp, 315_000);
});

test("XIRR and projected engine return an annualized rate", () => {
  const xirr = calculateXirr([
    { date: "2025-01-01", amount: -100 },
    { date: "2026-01-01", amount: 110 },
  ]);
  assert.ok(xirr !== null && Math.abs(xirr - 0.1) < 0.001);
  assert.notEqual(projectedInvestmentIrr(project(), 10), null);
});

test("bono pie and IVA refund reduce net capital without hiding purchase cash", () => {
  const investment = project({
    down_payment_clp: 40_000_000,
    down_payment_bonus_clp: 10_000_000,
    property_value_clp: 200_000_000,
    closing_cost_rate: 0.02,
    iva_refund_clp: 8_000_000,
    iva_refund_status: "approved",
  });
  const summary = plannedAcquisitionSummary(investment);
  assert.equal(summary.cashDownPayment, 30_000_000);
  assert.equal(summary.cashRequiredAtPurchase, 34_000_000);
  assert.equal(summary.netCapitalAfterRefund, 26_000_000);
});

test("DFL2 distinguishes the first two homes and the optional 2027 regime", () => {
  const exempt = project({ dfl2_qualified: true, property_surface_m2: 60, dfl2_property_number: 2, acquisition_owner_type: "natural_person", estimated_income_tax_rate: 0.2 });
  assert.equal(dfl2Assessment(exempt, "2026-11-15").effectiveTaxRate, 0);
  const third = project({ ...exempt, dfl2_property_number: 3, use_dfl2_5pct_regime: true });
  assert.equal(dfl2Assessment(third, "2026-11-15").effectiveTaxRate, 0.2);
  assert.equal(dfl2Assessment(third, "2027-01-01").effectiveTaxRate, 0.05);
  assert.equal(dfl2Assessment(third, "2027-01").effectiveTaxRate, 0.05);
  assert.equal(dfl2Assessment({ ...third, acquisition_owner_type: "individual_business" }, "2026-12").currentlyExempt, false);
});
