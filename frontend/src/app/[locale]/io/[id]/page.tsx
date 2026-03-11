"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import Link from "next/link";
import { api, type IO, type IOVersion, type Source, type IOContent } from "@/lib/api";
import { CategoryBadge } from "@/components/CategoryBadge";
import { QualityConstellation } from "@/components/QualityConstellation";

function getContent(version: IOVersion | null, locale: string): IOContent | null {
  if (!version) return null;
  return (version as any)[`content_${locale}`] || version.content_de || version.content_en;
}

export default function IODetailPage({ params }: { params: { id: string } }) {
  const locale = useLocale();
  const t = useTranslations("io");
  const [io, setIO] = useState<IO | null>(null);
  const [versions, setVersions] = useState<IOVersion[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [activeTab, setActiveTab] = useState<"content" | "sources" | "versions">("content");

  useEffect(() => {
    api.getIO(params.id).then(setIO).catch(console.error);
    api.getIOVersions(params.id).then(setVersions).catch(console.error);
    api.getIOSources(params.id).then(setSources).catch(console.error);
  }, [params.id]);

  if (!io) {
    return <div className="animate-pulse card h-96" />;
  }

  const content = getContent(io.current_version, locale);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main content */}
      <div className="lg:col-span-2 space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <CategoryBadge category={io.category} />
            <span className="text-sm text-gray-500">{io.scope}</span>
            {io.canton_codes?.map((c) => (
              <span key={c} className="badge bg-gray-100 dark:bg-gray-800 text-gray-600">{c}</span>
            ))}
          </div>

          <h1 className="text-3xl font-serif font-bold leading-tight">
            {content?.title || "Untitled"}
          </h1>

          {content?.lead && (
            <p className="text-lg text-gray-600 dark:text-gray-400 mt-3 font-serif italic">
              {content.lead}
            </p>
          )}

          <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
            <span>{t("versions")}: {io.version_count}</span>
            <span>{t("sources")}: {sources.length}</span>
            {io.first_reported_at && (
              <time>{new Date(io.first_reported_at).toLocaleDateString(locale)}</time>
            )}
          </div>
        </div>

        {/* Tab bar */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {(["content", "sources", "versions"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab
                  ? "border-signal-blue text-signal-blue"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t(tab === "content" ? "title" : tab)}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === "content" && content && (
          <article className="prose dark:prose-invert max-w-none">
            {content.sections.map((section, i) => (
              <div key={i} className="mb-6">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-2">
                  {section.type.replace("_", " ")}
                </h3>
                <div className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {section.content}
                </div>
                {section.attributions && section.attributions.length > 0 && (
                  <div className="text-xs text-gray-400 mt-2">
                    {section.attributions.join(" | ")}
                  </div>
                )}
              </div>
            ))}
          </article>
        )}

        {activeTab === "sources" && (
          <div className="space-y-3">
            {sources.map((source) => (
              <div key={source.id} className="card">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{source.original_title || "Source"}</h4>
                    <p className="text-sm text-gray-500 mt-1">{source.attribution_text}</p>
                    {source.snippet && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-3">
                        {source.snippet}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="badge bg-gray-100 dark:bg-gray-800 text-xs">
                      {source.source_type}
                    </span>
                    {source.publisher_reliability_score != null && (
                      <span className="text-xs text-gray-400 font-mono">
                        {Math.round(source.publisher_reliability_score * 100)}%
                      </span>
                    )}
                  </div>
                </div>
                <a
                  href={source.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-signal-blue hover:underline mt-2 block"
                >
                  {source.original_url}
                </a>
              </div>
            ))}
          </div>
        )}

        {activeTab === "versions" && (
          <div className="space-y-3">
            {versions.map((v) => {
              const vc = getContent(v, locale);
              return (
                <div key={v.id} className="card">
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-mono font-bold">v{v.version_number}</span>
                      <span className="mx-2 text-gray-400">|</span>
                      <span className="text-sm text-gray-500">{v.trigger_type}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`badge ${v.review_status === "approved" ? "bg-green-100 text-green-800" : v.review_status === "rejected" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"}`}>
                        {v.review_status}
                      </span>
                      <time className="text-xs text-gray-400">
                        {new Date(v.created_at).toLocaleString(locale)}
                      </time>
                    </div>
                  </div>
                  {vc && <p className="text-sm text-gray-600 mt-2">{vc.title}</p>}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        <QualityConstellation
          confirmationDensity={io.confirmation_density}
          sourceDiversity={io.source_diversity}
          completeness={io.completeness_score}
        />

        {/* Bias Spectrum */}
        {Object.keys(io.bias_spectrum).length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              {t("biasSpectrum")}
            </h3>
            <div className="space-y-2">
              {Object.entries(io.bias_spectrum).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-300 capitalize">{key.replace("_", " ")}</span>
                  <span className="font-mono">{Math.round(value * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Missing Elements */}
        {io.missing_elements && io.missing_elements.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              {t("missingVoices")}
            </h3>
            <ul className="space-y-1">
              {io.missing_elements.map((el, i) => (
                <li key={i} className="text-sm text-amber-600 dark:text-amber-400 flex items-start gap-2">
                  <span className="mt-1">?</span>
                  <span>{el}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
