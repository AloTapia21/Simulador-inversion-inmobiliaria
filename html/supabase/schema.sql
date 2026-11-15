create extension if not exists pgcrypto;

create table if not exists public.investment_projects (
  id uuid primary key default gen_random_uuid(),
  owner_id text not null,
  name text not null,
  address text not null default '',
  status text not null default 'active' check (status in ('active', 'planning', 'sold')),
  purchase_date date not null,
  uf_value numeric not null default 0,
  property_value_uf numeric not null default 0,
  property_value_clp numeric not null default 0,
  down_payment_clp numeric not null default 0,
  mortgage_amount_clp numeric not null default 0,
  annual_mortgage_rate numeric not null default 0,
  mortgage_term_years integer not null default 30,
  monthly_payment_estimated numeric not null default 0,
  initial_rent_estimated numeric not null default 0,
  rent_growth_annual numeric not null default 0,
  vacancy_rate_estimated numeric not null default 0,
  admin_rate_estimated numeric not null default 0,
  monthly_common_expenses_estimated numeric not null default 0,
  common_expenses_growth_annual numeric not null default 0.03,
  annual_contributions_estimated numeric not null default 0,
  contributions_growth_annual numeric not null default 0.03,
  annual_insurance_estimated numeric not null default 0,
  insurance_growth_annual numeric not null default 0.03,
  maintenance_rate_estimated numeric not null default 0,
  periodic_expense_interval_years integer not null default 5,
  periodic_expense_clp numeric not null default 0,
  periodic_expense_growth_annual numeric not null default 0.03,
  annual_appreciation_rate numeric not null default 0,
  closing_cost_rate numeric not null default 0,
  sale_cost_rate numeric not null default 0,
  iva_refund_clp numeric not null default 0,
  planned_sale_year integer not null default 10,
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists investment_projects_owner_idx
  on public.investment_projects (owner_id, updated_at desc);

alter table public.investment_projects
  add column if not exists common_expenses_growth_annual numeric not null default 0.03,
  add column if not exists contributions_growth_annual numeric not null default 0.03,
  add column if not exists insurance_growth_annual numeric not null default 0.03,
  add column if not exists periodic_expense_interval_years integer not null default 5,
  add column if not exists periodic_expense_clp numeric not null default 0,
  add column if not exists periodic_expense_growth_annual numeric not null default 0.03;

create table if not exists public.investment_monthly_records (
  id uuid primary key default gen_random_uuid(),
  owner_id text not null,
  project_id uuid not null references public.investment_projects(id) on delete cascade,
  period date not null,
  rent_collected numeric not null default 0,
  mortgage_payment numeric not null default 0,
  vacancy_days integer not null default 0 check (vacancy_days between 0 and 31),
  admin_fee numeric not null default 0,
  common_expenses numeric not null default 0,
  contributions numeric not null default 0,
  insurance numeric not null default 0,
  maintenance numeric not null default 0,
  repairs numeric not null default 0,
  other_expenses numeric not null default 0,
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, period)
);

create index if not exists investment_records_owner_project_idx
  on public.investment_monthly_records (owner_id, project_id, period desc);

create index if not exists investment_records_project_idx
  on public.investment_monthly_records (project_id);

alter table public.investment_projects enable row level security;
alter table public.investment_monthly_records enable row level security;

revoke all on public.investment_projects from anon, authenticated;
revoke all on public.investment_monthly_records from anon, authenticated;
grant select, insert, update, delete on public.investment_projects to authenticated;
grant select, insert, update, delete on public.investment_monthly_records to authenticated;

drop policy if exists "projects_select_own" on public.investment_projects;
create policy "projects_select_own" on public.investment_projects
  for select to authenticated using (owner_id = (select auth.uid())::text);

drop policy if exists "projects_insert_own" on public.investment_projects;
create policy "projects_insert_own" on public.investment_projects
  for insert to authenticated with check (owner_id = (select auth.uid())::text);

drop policy if exists "projects_update_own" on public.investment_projects;
create policy "projects_update_own" on public.investment_projects
  for update to authenticated
  using (owner_id = (select auth.uid())::text)
  with check (owner_id = (select auth.uid())::text);

drop policy if exists "projects_delete_own" on public.investment_projects;
create policy "projects_delete_own" on public.investment_projects
  for delete to authenticated using (owner_id = (select auth.uid())::text);

drop policy if exists "records_select_own" on public.investment_monthly_records;
create policy "records_select_own" on public.investment_monthly_records
  for select to authenticated using (owner_id = (select auth.uid())::text);

drop policy if exists "records_insert_own" on public.investment_monthly_records;
create policy "records_insert_own" on public.investment_monthly_records
  for insert to authenticated with check (
    owner_id = (select auth.uid())::text
    and exists (
      select 1 from public.investment_projects p
      where p.id = project_id and p.owner_id = (select auth.uid())::text
    )
  );

drop policy if exists "records_update_own" on public.investment_monthly_records;
create policy "records_update_own" on public.investment_monthly_records
  for update to authenticated
  using (owner_id = (select auth.uid())::text)
  with check (
    owner_id = (select auth.uid())::text
    and exists (
      select 1 from public.investment_projects p
      where p.id = project_id and p.owner_id = (select auth.uid())::text
    )
  );

drop policy if exists "records_delete_own" on public.investment_monthly_records;
create policy "records_delete_own" on public.investment_monthly_records
  for delete to authenticated using (owner_id = (select auth.uid())::text);

comment on table public.investment_projects is
  'Supuestos y datos base de cada inversión inmobiliaria, aislados por usuario de Supabase Auth.';
comment on table public.investment_monthly_records is
  'Resultados reales mensuales de arriendo, dividendo, vacancia y desembolsos.';
