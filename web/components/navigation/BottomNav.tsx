"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// Sourced from design-reference: every mockup with a bottom nav
// (home_dashboard, insights_dashboard, reproductive_health, profile_privacy,
// streak_rewards) shows this same 3-tab set with these EXACT Material
// Symbols Outlined ligature names — confirmed identical across all of them,
// not a guessed equivalent:
//   home_dashboard/code.html:335      <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">home</span>
//   reproductive_health/code.html:334 <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">calendar_today</span>
//   profile_privacy/code.html:303     <span class="material-symbols-outlined ..." style="font-variation-settings: 'FILL' 1;">person</span>
// The active tab's icon uses FILL 1 (solid), inactive tabs use FILL 0
// (outlined) — that fill toggle is the mockups' only active/inactive icon
// treatment, so it's reproduced exactly rather than approximated with a
// color-only or scale-only state change.
//
// The "Profile" tab points at /settings, not /profile: design-reference's
// own profile_privacy/code.html — the mockup this tab represents — is
// titled "Arohi - Settings", and that's the page that actually exists now.
const TABS = [
  { href: "/dashboard", label: "Home", icon: "home" },
  { href: "/calendar", label: "Calendar", icon: "calendar_today" },
  { href: "/settings", label: "Profile", icon: "person" },
] as const;

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-50 flex items-center justify-around border-t border-border bg-surface px-6 pb-6 pt-2 shadow-sm"
    >
      {TABS.map((tab) => {
        const isActive = pathname === tab.href || pathname?.startsWith(`${tab.href}/`);

        return (
          <Link
            key={tab.href}
            href={tab.href}
            aria-current={isActive ? "page" : undefined}
            className={`flex min-h-[48px] min-w-[48px] flex-col items-center justify-center gap-0.5 rounded-xl px-2 py-1 text-xs font-semibold transition-colors ${
              isActive ? "bg-brand-blush text-brand-deep" : "text-foreground/70 hover:bg-brand-blush/50"
            }`}
          >
            <span
              aria-hidden="true"
              className="material-symbols-outlined text-2xl leading-none"
              style={{ fontVariationSettings: `'FILL' ${isActive ? 1 : 0}` }}
            >
              {tab.icon}
            </span>
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
