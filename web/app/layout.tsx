import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Nunito_Sans } from "next/font/google";
import "./globals.css";

const nunitoSans = Nunito_Sans({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  variable: "--font-nunito-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Arohi",
  description: "A women's wellness companion.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={nunitoSans.variable}>
      <head>
        {/* Exact URL every design-reference mockup loads this font from
            (e.g. home_dashboard/code.html) — without it, a
            material-symbols-outlined span just renders its ligature text
            literally ("home", "calendar_today", "person") instead of an
            icon glyph. next/font/google has no entry for this font (it's a
            variable icon font, not a text font — confirmed there's no
            Material_Symbols_Outlined export), so a plain <link> is the only
            option. eslint-disable-next-line: @next/next/no-page-custom-font
            is a Pages-Router-era rule about per-page font scoping in
            pages/_document.js; it doesn't apply to App Router's
            app/layout.tsx, where a <link> here is Next's own documented
            pattern and is hoisted/deduped across every route. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans">{children}</body>
    </html>
  );
}
