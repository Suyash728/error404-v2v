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
      <body className="font-sans">{children}</body>
    </html>
  );
}
