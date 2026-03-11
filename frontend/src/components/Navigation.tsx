"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth, useTheme } from "@/lib/store";
import { useEffect } from "react";

const navItems = [
  { key: "home", href: "/", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { key: "search", href: "/search", icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" },
  { key: "brief", href: "/brief", icon: "M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" },
  { key: "votes", href: "/votes", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" },
  { key: "entities", href: "/entities", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" },
];

export function Navigation() {
  const t = useTranslations("nav");
  const tc = useTranslations("common");
  const pathname = usePathname();
  const { user, init, logout } = useAuth();
  const { dark, toggle } = useTheme();

  useEffect(() => {
    init();
  }, [init]);

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-signal-navy dark:bg-signal-dark-bg border-r border-gray-800 hidden md:flex flex-col z-50">
      {/* Logo */}
      <div className="p-6">
        <Link href="/" className="block">
          <h1 className="text-2xl font-bold text-white tracking-tight">
            SIGNAL<span className="text-signal-red">.CH</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1">{tc("tagline")}</p>
        </Link>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === `/${item.href}` || pathname?.endsWith(item.href);
          return (
            <Link
              key={item.key}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-signal-blue text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
              </svg>
              {t(item.key)}
            </Link>
          );
        })}

        {user?.is_admin && (
          <Link
            href="/admin"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {t("admin")}
          </Link>
        )}
      </nav>

      {/* Bottom: Theme toggle + Auth */}
      <div className="p-4 border-t border-gray-800 space-y-3">
        <button
          onClick={toggle}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-800"
        >
          {dark ? tc("lightMode") : tc("darkMode")}
        </button>

        {user ? (
          <div className="space-y-2">
            <p className="text-sm text-gray-400 px-3 truncate">{user.display_name || user.email}</p>
            <button
              onClick={logout}
              className="w-full px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-800 text-left"
            >
              {tc("logout")}
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="block w-full px-3 py-2 rounded-lg text-sm text-center bg-signal-blue text-white hover:bg-blue-700"
          >
            {tc("login")}
          </Link>
        )}
      </div>
    </aside>
  );
}
