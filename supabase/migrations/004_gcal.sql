-- Google Calendar sync (CC-13): OAuth tokens + idempotency tracking for
-- prediction-derived events. Reminders already have their own
-- gcal_event_id column from 001_init.sql, so they don't need a row here.

create table public.gcal_tokens (
  user_id uuid primary key references auth.users (id) on delete cascade,
  refresh_token_encrypted text not null,
  calendar_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.gcal_tokens enable row level security;
-- Intentionally no policies for anon/authenticated: this table holds
-- encrypted OAuth refresh tokens and is backend-only. service_role
-- bypasses RLS by design (core/supabase.py) for all access; RLS stays
-- enabled per this schema's "every table has RLS" convention, it's just
-- deliberately policy-less for direct client access.

create table public.gcal_synced_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  event_key text not null,
  gcal_event_id text not null,
  updated_at timestamptz not null default now(),
  unique (user_id, event_key)
);

alter table public.gcal_synced_events enable row level security;
-- Same reasoning as gcal_tokens above: backend-only bookkeeping, no
-- authenticated/anon policies.

-- Explicit grants rather than relying solely on 002_grants.sql's ALTER
-- DEFAULT PRIVILEGES carrying over automatically to new tables — this
-- project already hit "permission denied for table" once from assuming
-- that, so being explicit here is cheap insurance.
grant all on public.gcal_tokens, public.gcal_synced_events to service_role;
