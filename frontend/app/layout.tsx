import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Meridian Home | Market Entry Analysis",
  description:
    "A market entry analysis for a simulated specialty retailer, picking the best two of five US metros to expand into next.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-white text-[#0b0b0b]">
        <header className="border-b border-[#e1e0d9] sticky top-0 bg-white/95 backdrop-blur z-50">
          <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
            <Link href="/" className="font-semibold text-[#0D1B2A]">
              Meridian Home{" "}
              <span className="text-[#898781] font-normal">| Market Entry Analysis</span>
            </Link>
            <nav className="hidden sm:flex gap-6 text-sm text-[#52514E]">
              <a href="#analysis" className="hover:text-[#0D1B2A]">
                Analysis
              </a>
              <a href="#financial" className="hover:text-[#0D1B2A]">
                Financial Model
              </a>
              <a href="#methodology" className="hover:text-[#0D1B2A]">
                Methodology
              </a>
              <a href="#downloads" className="hover:text-[#0D1B2A]">
                Downloads
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-[#e1e0d9] py-6 text-center text-xs text-[#898781]">
          Meridian Home Market Entry Analysis — Masters in Business Analytics portfolio project
        </footer>
      </body>
    </html>
  );
}
