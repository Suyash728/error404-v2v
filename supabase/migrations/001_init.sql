-- Arohi initial schema.
-- Every user-owned table has RLS enabled with (select auth.uid()) = user_id (or = id
-- for profiles, whose primary key *is* the auth.users id, and = user_id for
-- gamification, whose primary key is user_id itself). rag_documents/rag_chunks
-- are shared reference content, not user-owned, so they get a read-only
-- policy for any authenticated user instead.

create extension if not exists pgcrypto;
create extension if not exists vector;

-- profiles ------------------------------------------------------------------

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text,
  avg_cycle_len smallint not null default 28,
  avg_period_len smallint not null default 5,
  last_period_start date,
  language_pref text not null default 'en',
  intention_mode text not null default 'track'
    check (intention_mode in ('track', 'avoid', 'ttc')),
  gcal_connected boolean not null default false,
  gfit_connected boolean not null default false,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

create policy "profiles_select_own" on public.profiles
  for select to authenticated
  using ((select auth.uid()) = id);

create policy "profiles_insert_own" on public.profiles
  for insert to authenticated
  with check ((select auth.uid()) = id);

create policy "profiles_update_own" on public.profiles
  for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

create policy "profiles_delete_own" on public.profiles
  for delete to authenticated
  using ((select auth.uid()) = id);

-- cycles ----------------------------------------------------------------

create table public.cycles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  start_date date not null,
  end_date date,
  length smallint
);

create index cycles_user_id_start_date_idx
  on public.cycles (user_id, start_date);

alter table public.cycles enable row level security;

create policy "cycles_select_own" on public.cycles
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "cycles_insert_own" on public.cycles
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "cycles_update_own" on public.cycles
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "cycles_delete_own" on public.cycles
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- daily_logs ------------------------------------------------------------

create table public.daily_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  log_date date not null,
  flow smallint check (flow between 0 and 4),
  symptoms text[] not null default '{}',
  mood smallint check (mood between 1 and 5),
  energy smallint check (energy between 1 and 5),
  water_ml int,
  bbt numeric(4, 1),
  notes text,
  unique (user_id, log_date)
);

-- The unique constraint above already creates a btree index on
-- (user_id, log_date), which covers the requested lookup/range index too —
-- a second identical index would just be dead weight, so none is added.

alter table public.daily_logs enable row level security;

create policy "daily_logs_select_own" on public.daily_logs
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "daily_logs_insert_own" on public.daily_logs
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "daily_logs_update_own" on public.daily_logs
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "daily_logs_delete_own" on public.daily_logs
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- reproductive_logs -------------------------------------------------------

create table public.reproductive_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  log_date date not null,
  contraception_taken boolean,
  cervical_mucus text,
  intercourse boolean,
  notes text
);

create index reproductive_logs_user_id_log_date_idx
  on public.reproductive_logs (user_id, log_date);

alter table public.reproductive_logs enable row level security;

create policy "reproductive_logs_select_own" on public.reproductive_logs
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "reproductive_logs_insert_own" on public.reproductive_logs
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "reproductive_logs_update_own" on public.reproductive_logs
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "reproductive_logs_delete_own" on public.reproductive_logs
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- reminders ---------------------------------------------------------------

create table public.reminders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  kind text not null
    check (kind in ('period', 'fertile', 'contraception', 'appointment')),
  title text not null,
  time_of_day time,
  frequency text,
  gcal_event_id text,
  discreet boolean not null default false
);

create index reminders_user_id_idx
  on public.reminders (user_id);

alter table public.reminders enable row level security;

create policy "reminders_select_own" on public.reminders
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "reminders_insert_own" on public.reminders
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "reminders_update_own" on public.reminders
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "reminders_delete_own" on public.reminders
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- risk_flags ----------------------------------------------------------------

create table public.risk_flags (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  flag_type text not null,
  severity text not null check (severity in ('low', 'medium', 'high')),
  fired_rules jsonb not null default '[]',
  explanation text,
  llm_provider text,
  created_at timestamptz not null default now()
);

create index risk_flags_user_id_created_at_idx
  on public.risk_flags (user_id, created_at);

alter table public.risk_flags enable row level security;

-- Append-only audit log: users may read and create their own flags, but
-- never update or delete them, so no update/delete policies exist.
create policy "risk_flags_select_own" on public.risk_flags
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "risk_flags_insert_own" on public.risk_flags
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

-- gamification --------------------------------------------------------------

create table public.gamification (
  user_id uuid primary key references auth.users (id) on delete cascade,
  petals int not null default 0,
  level text default 'Seedling',
  streak_count int not null default 0,
  streak_freeze_used boolean not null default false,
  last_checkin date
);

alter table public.gamification enable row level security;

create policy "gamification_select_own" on public.gamification
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "gamification_insert_own" on public.gamification
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "gamification_update_own" on public.gamification
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "gamification_delete_own" on public.gamification
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- badges ----------------------------------------------------------------

create table public.badges (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  badge_key text not null,
  earned_at timestamptz not null default now(),
  unique (user_id, badge_key)
);

create index badges_user_id_idx
  on public.badges (user_id);

alter table public.badges enable row level security;

create policy "badges_select_own" on public.badges
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "badges_insert_own" on public.badges
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "badges_update_own" on public.badges
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "badges_delete_own" on public.badges
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- fit_snapshots (demo) --------------------------------------------------

create table public.fit_snapshots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  date date not null,
  steps int,
  active_min int,
  sleep_min int,
  avg_hr int
);

create index fit_snapshots_user_id_date_idx
  on public.fit_snapshots (user_id, date);

alter table public.fit_snapshots enable row level security;

create policy "fit_snapshots_select_own" on public.fit_snapshots
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "fit_snapshots_insert_own" on public.fit_snapshots
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "fit_snapshots_update_own" on public.fit_snapshots
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "fit_snapshots_delete_own" on public.fit_snapshots
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- rag_documents / rag_chunks ----------------------------------------------
-- Shared knowledge base for retrieval-augmented Sakhi answers. Not user-owned,
-- so RLS here is read-only for any authenticated user; writes happen through
-- the backend's service-role key, which bypasses RLS entirely.

create table public.rag_documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source_org text
);

alter table public.rag_documents enable row level security;

create policy "rag_documents_select_authenticated" on public.rag_documents
  for select to authenticated
  using (true);

create table public.rag_chunks (
  id uuid primary key default gen_random_uuid(),
  doc_id uuid not null references public.rag_documents (id) on delete cascade,
  content text not null,
  embedding vector(384)
);

-- HNSW builds fine on an empty table; ivfflat needs data present to pick
-- good centroids, which we don't have yet.
create index rag_chunks_embedding_hnsw_idx
  on public.rag_chunks
  using hnsw (embedding vector_cosine_ops);

alter table public.rag_chunks enable row level security;

create policy "rag_chunks_select_authenticated" on public.rag_chunks
  for select to authenticated
  using (true);

-- signup bootstrap ---------------------------------------------------------
-- Every auth.users row gets a matching profiles + gamification row created
-- automatically. Both inserts touch only their identity column (id/user_id),
-- so every other column falls back to its table default and this can never
-- fail in a way that blocks signup.

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id) values (new.id)
  on conflict (id) do nothing;

  insert into public.gamification (user_id) values (new.id)
  on conflict (user_id) do nothing;

  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();
