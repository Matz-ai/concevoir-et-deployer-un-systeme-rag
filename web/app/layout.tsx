import type { Metadata, Viewport } from "next";
import { Bricolage_Grotesque, Instrument_Sans } from "next/font/google";
import Logo from "@/components/Logo.tsx";
import "./globals.css";

// Instrument Sans pour le texte, Bricolage Grotesque pour les titres ; servies par Next, sans appel à Google
const corps = Instrument_Sans({ subsets: ["latin"], display: "swap", variable: "--police" });
const titres = Bricolage_Grotesque({ subsets: ["latin"], display: "swap", weight: ["500", "700"], variable: "--police-titre" });

export const metadata: Metadata = {
  title: "Puls-Events — l'assistant sorties du 93",
  description: "Puls recommande des évènements culturels en Seine-Saint-Denis à partir de l'agenda OpenAgenda.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${corps.variable} ${titres.variable}`}>
      <body>
        <header className="bandeau">
          <a href="/" aria-label="Puls-Events, nouvelle conversation">
            <Logo />
          </a>
          <span className="bandeau-sous-titre">L'assistant sorties de la Seine-Saint-Denis</span>
        </header>
        {children}
      </body>
    </html>
  );
}
