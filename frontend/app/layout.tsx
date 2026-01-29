import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Test Suite Generator",
  description: "AI-powered test generation for OpenAPI specs and Python functions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-stone-100">
        {children}
      </body>
    </html>
  );
}
