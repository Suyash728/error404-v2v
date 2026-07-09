import { createClient } from "@/lib/supabase/server";

export default async function HomePage() {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 px-6 py-12">
      <h1 className="text-2xl font-semibold text-foreground">
        Hi{user?.email ? `, ${user.email}` : ""} — Sakhi is here.
      </h1>
      <p className="text-foreground/70">
        Your cycle insights and companion guidance will live here.
      </p>
    </main>
  );
}
