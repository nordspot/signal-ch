"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { api, type IO, type IOListResponse } from "@/lib/api";
import { IOCard } from "@/components/IOCard";
import { CategoryBadge } from "@/components/CategoryBadge";

const CATEGORIES = [
  "politics", "economy", "society", "health", "environment",
  "technology", "legal", "infrastructure", "international",
];

export default function HomePage() {
  const t = useTranslations("nav");
  const tc = useTranslations("categories");
  const [data, setData] = useState<IOListResponse | null>(null);
  const [category, setCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = { status: "published" };
    if (category) params.category = category;

    api.listIOs(params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold">
          SIGNAL<span className="text-signal-red">.CH</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          {t("feed")}
        </p>
      </div>

      {/* Category filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setCategory("")}
          className={`badge ${!category ? "bg-signal-blue text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"} cursor-pointer`}
        >
          Alle
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === category ? "" : cat)}
            className={`badge cursor-pointer ${cat === category ? "bg-signal-blue text-white" : ""}`}
          >
            {tc(cat as any)}
          </button>
        ))}
      </div>

      {/* IO List */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-3" />
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
            </div>
          ))}
        </div>
      ) : data?.items.length ? (
        <div className="space-y-4">
          {data.items.map((io) => (
            <IOCard key={io.id} io={io} />
          ))}
          {data.total > data.page_size && (
            <p className="text-center text-sm text-gray-500">
              {data.items.length} / {data.total}
            </p>
          )}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No intelligence objects yet. Start the ingestion pipeline to populate data.</p>
        </div>
      )}
    </div>
  );
}
