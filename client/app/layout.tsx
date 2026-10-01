import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/providers/QueryProvider";
import Navbar from "@/components/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RetainIQ | Customer Intelligence Platform",
  description: "E-Commerce Customer Intelligence & Churn Prediction Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex bg-slate-950 text-slate-100">
        <QueryProvider>
          <Navbar />
          <main className="flex-1 p-8 overflow-y-auto bg-slate-950">{children}</main>
        </QueryProvider>
      </body>
    </html>
  );
}
