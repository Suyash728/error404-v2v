-- Fixes: profiles_service.get_profile() returning zero rows for accounts
-- that signed up before 001_init.sql's on_auth_user_created trigger
-- existed (the trigger only fires on new auth.users inserts — it can't
-- retroactively cover accounts created earlier). Mirrors handle_new_user()
-- exactly, including its on-conflict-do-nothing semantics, so this is safe
-- to run any number of times against any state of the users table.

insert into public.profiles (id)
select id from auth.users
on conflict (id) do nothing;

insert into public.gamification (user_id)
select id from auth.users
on conflict (user_id) do nothing;
