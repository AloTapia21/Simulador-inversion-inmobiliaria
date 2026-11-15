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
  current_market_value_uf numeric not null default 0,
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
  add column if not exists current_market_value_uf numeric not null default 0,
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

create table if not exists public.investment_project_members (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.investment_projects(id) on delete cascade,
  user_id text,
  invited_email text,
  display_name text not null,
  role text not null default 'editor' check (role in ('owner', 'editor', 'viewer')),
  ownership_percentage numeric not null default 0 check (ownership_percentage between 0 and 100),
  created_by text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, id),
  check (user_id is not null or invited_email is not null)
);

create unique index if not exists investment_members_project_user_unique
  on public.investment_project_members (project_id, user_id)
  where user_id is not null;
create unique index if not exists investment_members_project_email_unique
  on public.investment_project_members (project_id, lower(invited_email))
  where invited_email is not null;
create index if not exists investment_members_project_idx
  on public.investment_project_members (project_id, created_at);
create index if not exists investment_members_email_idx
  on public.investment_project_members (lower(invited_email))
  where invited_email is not null;

insert into public.investment_project_members (
  project_id, user_id, display_name, role, ownership_percentage, created_by
)
select p.id, p.owner_id, 'Propietario', 'owner', 100, p.owner_id
from public.investment_projects p
where not exists (
  select 1 from public.investment_project_members m
  where m.project_id = p.id and m.user_id = p.owner_id
);

create table if not exists public.investment_transactions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.investment_projects(id) on delete cascade,
  transaction_date date not null,
  category text not null check (category in (
    'rent', 'iva_refund', 'other_income', 'down_payment', 'closing_costs', 'mortgage',
    'administration', 'common_expenses', 'contributions', 'insurance', 'maintenance',
    'repairs', 'furnishing', 'other_expense'
  )),
  direction text not null check (direction in ('income', 'expense')),
  amount_clp numeric not null check (amount_clp > 0),
  uf_value numeric not null check (uf_value > 0),
  amount_uf numeric not null check (amount_uf > 0),
  notes text not null default '',
  created_by text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, id)
);

create index if not exists investment_transactions_project_date_idx
  on public.investment_transactions (project_id, transaction_date desc, created_at desc);
create index if not exists investment_transactions_project_category_idx
  on public.investment_transactions (project_id, category, transaction_date desc);

create table if not exists public.investment_transaction_splits (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null,
  transaction_id uuid not null,
  member_id uuid not null,
  amount_clp numeric not null check (amount_clp > 0),
  amount_uf numeric not null check (amount_uf > 0),
  created_at timestamptz not null default now(),
  foreign key (project_id, transaction_id)
    references public.investment_transactions(project_id, id) on delete cascade,
  foreign key (project_id, member_id)
    references public.investment_project_members(project_id, id) on delete restrict,
  unique (transaction_id, member_id)
);

create index if not exists investment_splits_project_member_idx
  on public.investment_transaction_splits (project_id, member_id);
create index if not exists investment_splits_transaction_idx
  on public.investment_transaction_splits (transaction_id);
create index if not exists investment_splits_project_transaction_idx
  on public.investment_transaction_splits (project_id, transaction_id);

create schema if not exists private;
revoke all on schema private from public, anon;

create or replace function private.has_investment_access(target_project_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.investment_projects p
    where p.id = target_project_id
      and p.owner_id = (select auth.uid())::text
  ) or exists (
    select 1
    from public.investment_project_members m
    where m.project_id = target_project_id
      and (
        m.user_id = (select auth.uid())::text
        or (
          m.invited_email is not null
          and lower(m.invited_email) = lower(coalesce((select auth.jwt() ->> 'email'), ''))
        )
      )
  );
$$;

create or replace function private.can_edit_investment(target_project_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.investment_projects p
    where p.id = target_project_id
      and p.owner_id = (select auth.uid())::text
  ) or exists (
    select 1
    from public.investment_project_members m
    where m.project_id = target_project_id
      and m.role in ('owner', 'editor')
      and (
        m.user_id = (select auth.uid())::text
        or (
          m.invited_email is not null
          and lower(m.invited_email) = lower(coalesce((select auth.jwt() ->> 'email'), ''))
        )
      )
  );
$$;

create or replace function private.owns_investment(target_project_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.investment_projects p
    where p.id = target_project_id and p.owner_id = (select auth.uid())::text
  );
$$;

revoke all on function private.has_investment_access(uuid) from public, anon;
revoke all on function private.can_edit_investment(uuid) from public, anon;
revoke all on function private.owns_investment(uuid) from public, anon;
grant usage on schema private to authenticated;
grant execute on function private.has_investment_access(uuid) to authenticated;
grant execute on function private.can_edit_investment(uuid) to authenticated;
grant execute on function private.owns_investment(uuid) to authenticated;

alter table public.investment_projects enable row level security;
alter table public.investment_monthly_records enable row level security;
alter table public.investment_project_members enable row level security;
alter table public.investment_transactions enable row level security;
alter table public.investment_transaction_splits enable row level security;

revoke all on public.investment_projects from anon, authenticated;
revoke all on public.investment_monthly_records from anon, authenticated;
revoke all on public.investment_project_members from anon, authenticated;
revoke all on public.investment_transactions from anon, authenticated;
revoke all on public.investment_transaction_splits from anon, authenticated;
grant select, insert, update, delete on public.investment_projects to authenticated;
grant select, insert, update, delete on public.investment_monthly_records to authenticated;
grant select, insert, update, delete on public.investment_project_members to authenticated;
grant select, insert, update, delete on public.investment_transactions to authenticated;
grant select, insert, update, delete on public.investment_transaction_splits to authenticated;

drop policy if exists "projects_select_own" on public.investment_projects;
create policy "projects_select_own" on public.investment_projects
  for select to authenticated using (
    owner_id = (select auth.uid())::text
    or (select private.has_investment_access(id))
  );

drop policy if exists "projects_insert_own" on public.investment_projects;
create policy "projects_insert_own" on public.investment_projects
  for insert to authenticated with check (owner_id = (select auth.uid())::text);

drop policy if exists "projects_update_own" on public.investment_projects;
create policy "projects_update_own" on public.investment_projects
  for update to authenticated
  using ((select private.can_edit_investment(id)))
  with check ((select private.can_edit_investment(id)));

drop policy if exists "projects_delete_own" on public.investment_projects;
create policy "projects_delete_own" on public.investment_projects
  for delete to authenticated using (owner_id = (select auth.uid())::text);

drop policy if exists "records_select_own" on public.investment_monthly_records;
create policy "records_select_own" on public.investment_monthly_records
  for select to authenticated using ((select private.has_investment_access(project_id)));

drop policy if exists "records_insert_own" on public.investment_monthly_records;
create policy "records_insert_own" on public.investment_monthly_records
  for insert to authenticated with check (
    owner_id = (select auth.uid())::text
    and (select private.can_edit_investment(project_id))
  );

drop policy if exists "records_update_own" on public.investment_monthly_records;
create policy "records_update_own" on public.investment_monthly_records
  for update to authenticated
  using ((select private.can_edit_investment(project_id)))
  with check (
    (select private.can_edit_investment(project_id))
  );

drop policy if exists "records_delete_own" on public.investment_monthly_records;
create policy "records_delete_own" on public.investment_monthly_records
  for delete to authenticated using ((select private.can_edit_investment(project_id)));

drop policy if exists "members_select_project" on public.investment_project_members;
create policy "members_select_project" on public.investment_project_members
  for select to authenticated using ((select private.has_investment_access(project_id)));

drop policy if exists "members_insert_owner" on public.investment_project_members;
create policy "members_insert_owner" on public.investment_project_members
  for insert to authenticated with check ((select private.owns_investment(project_id)));

drop policy if exists "members_update_owner" on public.investment_project_members;
create policy "members_update_owner" on public.investment_project_members
  for update to authenticated
  using ((select private.owns_investment(project_id)))
  with check ((select private.owns_investment(project_id)));

drop policy if exists "members_delete_owner" on public.investment_project_members;
create policy "members_delete_owner" on public.investment_project_members
  for delete to authenticated using ((select private.owns_investment(project_id)));

drop policy if exists "transactions_select_project" on public.investment_transactions;
create policy "transactions_select_project" on public.investment_transactions
  for select to authenticated using ((select private.has_investment_access(project_id)));

drop policy if exists "transactions_insert_project" on public.investment_transactions;
create policy "transactions_insert_project" on public.investment_transactions
  for insert to authenticated with check (
    created_by = (select auth.uid())::text
    and (select private.can_edit_investment(project_id))
  );

drop policy if exists "transactions_update_project" on public.investment_transactions;
create policy "transactions_update_project" on public.investment_transactions
  for update to authenticated
  using ((select private.can_edit_investment(project_id)))
  with check ((select private.can_edit_investment(project_id)));

drop policy if exists "transactions_delete_project" on public.investment_transactions;
create policy "transactions_delete_project" on public.investment_transactions
  for delete to authenticated using ((select private.can_edit_investment(project_id)));

drop policy if exists "splits_select_project" on public.investment_transaction_splits;
create policy "splits_select_project" on public.investment_transaction_splits
  for select to authenticated using ((select private.has_investment_access(project_id)));

drop policy if exists "splits_insert_project" on public.investment_transaction_splits;
create policy "splits_insert_project" on public.investment_transaction_splits
  for insert to authenticated with check ((select private.can_edit_investment(project_id)));

drop policy if exists "splits_update_project" on public.investment_transaction_splits;
create policy "splits_update_project" on public.investment_transaction_splits
  for update to authenticated
  using ((select private.can_edit_investment(project_id)))
  with check ((select private.can_edit_investment(project_id)));

drop policy if exists "splits_delete_project" on public.investment_transaction_splits;
create policy "splits_delete_project" on public.investment_transaction_splits
  for delete to authenticated using ((select private.can_edit_investment(project_id)));

comment on table public.investment_projects is
  'Supuestos y datos base de cada inversión inmobiliaria, aislados por usuario de Supabase Auth.';
comment on table public.investment_monthly_records is
  'Resultados reales mensuales de arriendo, dividendo, vacancia y desembolsos.';
comment on table public.investment_project_members is
  'Participantes con acceso y porcentaje económico en una inversión compartida.';
comment on table public.investment_transactions is
  'Movimientos reales con monto CLP y equivalencia UF histórica.';
comment on table public.investment_transaction_splits is
  'Distribución exacta de cada movimiento entre los participantes.';
