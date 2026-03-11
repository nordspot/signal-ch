"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { api, type IO, type IOListResponse } from "@/lib/api";
import { IOCard } from "@/components/IOCard";
import { CategoryBadge } from "@/components/CategoryBadge";

export default function BriefPage() {
  const t = useTranslations("brief");
  const locale = useLocale();
  const [data, setData] = useState<IOListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listIOs({ status: "published", page_size: "10" })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const today = new Date().toLocaleDateString(locale, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="max-w-2xl mx-auto">
      {/* Brief header */}
      <div className="text-center mb-10">
        <p className="text-sm text-gray-500 uppercase tracking-widest mb-2">
          {today}
        </p>
        <h1 className="text-3xl font-serif font-bold mb-2">
          {t("title")}
        </h1>
        <p className="text-gray-500 dark:text-gray-400">
          {t("goodMorning")}. Hier ist Ihr Signal-Briefing.
        </p>
      </div>

      {/* Divider */}
      <div className="flex items-center gap-4 mb-8">
        <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
        <span className="text-xs text-gray-400 uppercase tracking-wider">{t("topStories")}</span>
        <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
      </div>

      {loading ? (
        <div className="space-y-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-2" />
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
              <div className="h-px bg-gray-200 dark:bg-gray-700 mt-6" />
            </div>
          ))}
        </div>
      ) : data?.items.length ? (
        <div className="space-y-8">
          {data.items.map((io, idx) => (
            <div key={io.id}>
              <div className="flex items-start gap-4">
                <span className="text-2xl font-serif font-bold text-gray-300 dark:text-gray-600 mt-1">
                  {idx + 1}
                </span>
                <IOCard io={io} />
              </div>
              {idx < data.items.length - 1 && (
                <div className="h-px bg-gray-200 dark:bg-gray-700 mt-6" />
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 py-12">
          No stories yet. The ingestion pipeline will populate this brief.
        </p>
      )}

      {/* Footer */}
      <div className="text-center mt-12 py-8 border-t border-gray-200 dark:border-gray-700">
        <p className="text-sm text-gray-400">
          Bleiben Sie informiert. SIGNAL.CH
        </p>
      </div>
    </div>
  );
}
