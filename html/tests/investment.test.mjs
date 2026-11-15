import assert from "node:assert/strict";
import test from "node:test";
import {
  EMPTY_PROJECT,
  calculateXirr,
  currentInvestmentSnapshot,
  memberContributionSummary,
  mortgageBalance,
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
