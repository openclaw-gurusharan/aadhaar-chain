import type { Metadata } from "next";
import { Inter, Instrument_Serif } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";
import { ConditionalNavbar, ConditionalMainWrapper } from "@/components/layout/ConditionalNavbar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  variable: "--font-instrument-serif",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "Identity Agent Platform - Self-Sovereign Identity on Solana",
  description: "Decentralized identity platform powered by Solana and Claude Agent SDK",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${instrumentSerif.variable} font-sans antialiased`}>
        <Providers>
          <div className="min-h-screen bg-background">
            <ConditionalNavbar />
            <ConditionalMainWrapper>
              {children}
            </ConditionalMainWrapper>
          </div>
        </Providers>
      </body>
    </html>
  );
}
