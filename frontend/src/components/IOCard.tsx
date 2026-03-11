"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { CategoryBadge } from "./CategoryBadge";
import type { IO, IOContent } from "@/lib/api";

function getContent(io: IO, locale: string): IOContent | null {
  const version = io.current_version;
  if (!version) return null;
  return (version as any)[`content_${locale}`] || version.content_de || version.content_en;
}

export function IOCard({ io }: { io: IO }) {
  const locale = useLocale();
  const t = useTranslations("io");
  const content = getContent(io, locale);

  return (
    <Link href={`/io/${io.id}`} className="card block hover:shadow-md transition-shadow group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <CategoryBadge category={io.category} />
            {io.scope !== "national" && (
              <span className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                {io.canton_codes?.join(", ") || io.scope}
              </span>
            )}
          </div>

          <h3 className="text-lg font-serif font-semibold group-hover:text-signal-blue transition-colors line-clamp-2">
            {content?.title || "Untitled"}
          </h3>

          {content?.lead && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
              {content.lead}
            </p>
          )}
        </div>

        {/* Quality indicator dot */}
        <div className="flex flex-col items-center gap-1 pt-1">
          <div
            className={`w-3 h-3 rounded-full ${
              (io.confirmation_density ?? 0) > 0.7
                ? "bg-green-500"
                : (io.confirmation_density ?? 0) > 0.4
                ? "bg-amber-500"
                : "bg-gray-300"
            }`}
            title={`${t("confirmationDensity")}: ${Math.round((io.confirmation_density ?? 0) * 100)}%`}
          />
          <span className="text-xs text-gray-400 font-mono">
            {io.version_count}v
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
        <time>
          {io.first_reported_at
            ? new Date(io.first_reported_at).toLocaleDateString(locale)
            : new Date(io.created_at).toLocaleDateString(locale)}
        </time>
        {io.missing_elements && io.missing_elements.length > 0 && (
          <span className="text-amber-600 dark:text-amber-400">
            {io.missing_elements.length} {t("missingVoices").toLowerCase()}
          </span>
        )}
      </div>
    </Link>
  );
}
