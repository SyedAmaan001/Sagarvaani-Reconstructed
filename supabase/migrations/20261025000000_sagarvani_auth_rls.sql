-- =============================================================================
-- Sagarvani — Supabase PostgreSQL Migration
-- Auth RLS: user_profiles + user_queries tables with Row Level Security
-- =============================================================================

-- User profiles table (extended metadata beyond auth.users)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email       TEXT,
    stakeholder_role TEXT,
    display_name TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User queries audit table (mirrors backend SQLite runs for Supabase-side audit)
CREATE TABLE IF NOT EXISTS public.user_queries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    run_id      TEXT NOT NULL,
    query_text  TEXT NOT NULL,
    status      TEXT NOT NULL,
    stakeholder_role TEXT,
    location_lat DOUBLE PRECISION,
    location_lon DOUBLE PRECISION,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_queries   ENABLE ROW LEVEL SECURITY;

-- RLS Policies: user_profiles
-- Users can view their own profile only.
CREATE POLICY "users_read_own_profile"
    ON public.user_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile only.
CREATE POLICY "users_update_own_profile"
    ON public.user_profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Profile is auto-created on signup via trigger (see below).
CREATE POLICY "users_insert_own_profile"
    ON public.user_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- RLS Policies: user_queries
-- Users can read only their own queries.
CREATE POLICY "users_read_own_queries"
    ON public.user_queries
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert only queries attributed to themselves.
CREATE POLICY "users_insert_own_queries"
    ON public.user_queries
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- =============================================================================
-- Trigger: auto-create user_profile on new signup
-- =============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, stakeholder_role)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data ->> 'stakeholder_role'
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

-- Attach trigger to auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
