"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { api, type DashboardStats, type ReviewItem, type IOContent } from "@/lib/api";

export default function AdminPage() {
  const t = useTranslations("admin");
  const locale = useLocale();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [queue, setQueue] = useState<ReviewItem[]>([]);
  const [tab, setTab] = useState<"stats" | "queue">("stats");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getStats().then(setStats).catch(() => null),
      api.getReviewQueue().then((d) => setQueue(d.items)).catch(() => []),
    ]).finally(() => setLoading(false));
  }, []);

  async function handleReview(versionId: string, action: string) {
    try {
      await api.reviewVersion(versionId, action);
      setQueue((q) => q.filter((item) => item.version_id !== versionId));
      if (stats) {
        setStats({
          ...stats,
          pending_reviews: stats.pending_reviews - 1,
          published_ios: action === "approved" ? stats.published_ios + 1 : stats.published_ios,
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  function getContent(item: ReviewItem): IOContent | null {
    const key = `content_${locale}` as keyof ReviewItem;
    return (item[key] as IOContent) || item.content_de || item.content_en;
  }

  if (loading) {
    return <div className="card animate-pulse h-96" />;
  }

  return (
    <div>
      <h1 className="text-2xl font-serif font-bold mb-6">{t("title")}</h1>

      {/* Stats grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {[
            { label: t("totalIOs"), value: stats.total_ios },
            { label: t("publishedIOs"), value: stats.published_ios },
            { label: t("pendingReviews"), value: stats.pending_reviews, highlight: stats.pending_reviews > 0 },
            { label: t("totalSources"), value: stats.total_sources },
            { label: t("publishers"), value: stats.total_publishers },
            { label: t("totalUsers"), value: stats.total_users },
          ].map((s) => (
            <div key={s.label} className={`card text-center ${s.highlight ? "border-amber-400 dark:border-amber-600" : ""}`}>
              <p className="text-2xl font-bold font-mono">{s.value}</p>
              <p className="text-xs text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button
          onClick={() => setTab("stats")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === "stats" ? "border-signal-blue text-signal-blue" : "border-transparent text-gray-500"}`}
        >
          {t("stats")}
        </button>
        <button
          onClick={() => setTab("queue")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === "queue" ? "border-signal-blue text-signal-blue" : "border-transparent text-gray-500"}`}
        >
          {t("reviewQueue")} ({queue.length})
        </button>
      </div>

      {tab === "queue" && (
        <div className="space-y-4">
          {queue.length === 0 ? (
            <p className="text-center text-gray-500 py-12">No items pending review.</p>
          ) : (
            queue.map((item) => {
              const content = getContent(item);
              return (
                <div key={item.version_id} className="card">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm">v{item.version_number}</span>
                        <span className="badge bg-gray-100 dark:bg-gray-800">{item.trigger_type}</span>
                        {item.io_category && (
                          <span className="badge bg-gray-100 dark:bg-gray-800">{item.io_category}</span>
                        )}
                      </div>
                      <h3 className="font-serif font-semibold text-lg">
                        {content?.title || "Untitled"}
                      </h3>
                    </div>
                    <time className="text-xs text-gray-400">
                      {item.created_at ? new Date(item.created_at).toLocaleString(locale) : ""}
                    </time>
                  </div>

                  {content?.lead && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{content.lead}</p>
                  )}

                  {content?.sections.map((section, i) => (
                    <div key={i} className="mb-2">
                      <span className="text-xs font-semibold uppercase text-gray-400">{section.type.replace("_", " ")}</span>
                      <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">{section.content}</p>
                    </div>
                  ))}

                  <div className="flex gap-2 mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={() => handleReview(item.version_id, "approved")}
                      className="btn-primary text-sm"
                    >
                      {t("approve")}
                    </button>
                    <button
                      onClick={() => handleReview(item.version_id, "rejected")}
                      className="btn-danger text-sm"
                    >
                      {t("reject")}
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {tab === "stats" && (
        <div className="card">
          <p className="text-gray-500">
            Detailed analytics dashboard with ingestion metrics, synthesis queue depth,
            editorial rejection rates, and business KPIs will be implemented in Phase 2.
          </p>
        </div>
      )}
    </div>
  );
}
