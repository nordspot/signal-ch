"use client";

import { useTranslations } from "next-intl";

const categoryColors: Record<string, string> = {
  politics: "badge-politics",
  economy: "badge-economy",
  health: "badge-health",
  environment: "badge-environment",
  technology: "badge-technology",
  society: "badge-society",
  legal: "badge-legal",
  sport: "badge-sport",
  culture: "badge-culture",
  science: "badge-science",
  education: "badge-education",
  infrastructure: "badge-infrastructure",
  international: "badge-international",
  local: "badge-local",
  opinion: "badge-society",
};

export function CategoryBadge({ category }: { category: string }) {
  const t = useTranslations("categories");
  const colorClass = categoryColors[category] || "badge-society";

  return (
    <span className={`badge ${colorClass}`}>
      {t(category as any)}
    </span>
  );
}
