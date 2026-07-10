import Link from "next/link";
import { apiServer } from "@/lib/api-server";
import { ConnectGoogleCalendar } from "@/components/settings/connect-google-calendar";

type Profile = {
  gcal_connected: boolean;
};

async function getProfile(): Promise<Profile | null> {
  try {
    return await apiServer.get<Profile>("/account/profile");
  } catch {
    return null;
  }
}

export default async function SettingsPage() {
  const profile = await getProfile();

  return (
    <main className="mx-auto flex max-w-[480px] flex-col gap-6 px-5 pb-28 pt-2">
      <header className="flex items-center">
        <Link
          href="/dashboard"
          aria-label="Back to dashboard"
          className="flex h-12 w-12 items-center justify-center rounded-full text-2xl text-brand-primary transition-opacity hover:opacity-80"
        >
          <span aria-hidden="true">←</span>
        </Link>
        <h1 className="flex-1 text-center text-xl font-extrabold text-brand-deep">Settings</h1>
        <span aria-hidden="true" className="h-12 w-12" />
      </header>

      <section aria-labelledby="connections-heading" className="flex flex-col gap-3">
        <h2 id="connections-heading" className="px-2 text-lg font-semibold text-foreground">
          Connections
        </h2>
        <ConnectGoogleCalendar initiallyConnected={profile?.gcal_connected ?? false} />
      </section>
    </main>
  );
}
