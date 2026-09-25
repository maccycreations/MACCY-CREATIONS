-- Add operational timestamps and safe update behavior.
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

drop trigger if exists profiles_updated_at on public.profiles;
create trigger profiles_updated_at before update on public.profiles for each row execute procedure public.set_updated_at();
drop trigger if exists settings_updated_at on public.user_settings;
create trigger settings_updated_at before update on public.user_settings for each row execute procedure public.set_updated_at();
drop trigger if exists app_data_updated_at on public.app_data;
create trigger app_data_updated_at before update on public.app_data for each row execute procedure public.set_updated_at();

-- The public API never exposes profiles globally; RLS restricts each row to auth.uid().
create index if not exists app_data_updated_idx on public.app_data(user_id, updated_at desc);
