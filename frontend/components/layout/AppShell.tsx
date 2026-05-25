"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AlertTriangle, BarChart3, Bell, CreditCard, FileUp, LogOut, Receipt, Settings, WalletCards } from "lucide-react";
import { clearToken } from "@/lib/api";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/import", label: "Import", icon: FileUp },
  { href: "/transactions", label: "Transactions", icon: Receipt },
  { href: "/subscriptions", label: "Subscriptions", icon: WalletCards },
  { href: "/bills", label: "Bills", icon: CreditCard },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Personal Finance Autopilot</div>
        <nav className="nav" aria-label="Primary">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} className={pathname === item.href ? "active" : ""} href={item.href}>
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </Link>
            );
          })}
          <button
            type="button"
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
          >
            <LogOut size={18} aria-hidden="true" />
            <span>Logout</span>
          </button>
        </nav>
        <div style={{ marginTop: 24, color: "#b8c8c0", fontSize: 13, lineHeight: 1.5 }}>
          <AlertTriangle size={16} aria-hidden="true" /> Estimates are based on imported data and are not financial advice.
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

