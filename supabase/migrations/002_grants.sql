-- Fixes: "permission denied for table X" (Postgres error 42501) from the
-- backend's service-role client, and would eventually hit the same wall for
-- authenticated/anon once anything queries as those roles.
--
-- On a normally-provisioned Supabase project, ALTER DEFAULT PRIVILEGES
-- already grants anon/authenticated/service_role baseline access to every
-- table in `public` — RLS (see 001_init.sql's `to authenticated` policies)
-- is what actually restricts authenticated, and service_role bypasses RLS
-- by design (core/supabase.py). This project's tables ended up without that
-- baseline grant, so 001_init.sql's policies currently have nothing to
-- gate: the role can't even reach the query to be filtered. This grants the
-- baseline explicitly instead of relying on it happening automatically, and
-- sets default privileges so future tables get it too.

grant usage on schema public to anon, authenticated, service_role;

grant all on all tables in schema public to service_role;
grant select, insert, update, delete on all tables in schema public to authenticated;

alter default privileges in schema public grant all on tables to service_role;
alter default privileges in schema public grant select, insert, update, delete on tables to authenticated;
