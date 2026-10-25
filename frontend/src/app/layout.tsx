import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const newsreader = Newsreader({
  variable: "--font-serif",
  subsets: ["latin"],
  display: "swap",
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "Sagarvani — Evidence-Aware Marine Decision Intelligence",
  description:
    "A clearer view of our ocean. Evidence-aware marine intelligence supporting coastal communities, fishers, port operators, and ocean researchers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${newsreader.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
