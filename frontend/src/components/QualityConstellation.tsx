"use client";

import { useTranslations } from "next-intl";

interface Props {
  confirmationDensity: number | null;
  sourceDiversity: number | null;
  completeness: number | null;
}

function Bar({ value, color }: { value: number; color: string }) {
  return (
    <div className="quality-bar">
      <div
        className={`quality-fill ${color}`}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  );
}

export function QualityConstellation({ confirmationDensity, sourceDiversity, completeness }: Props) {
  const t = useTranslations("io");

  const metrics = [
    { label: t("confirmationDensity"), value: confirmationDensity, color: "bg-green-500" },
    { label: t("sourceDiversity"), value: sourceDiversity, color: "bg-blue-500" },
    { label: t("completeness"), value: completeness, color: "bg-amber-500" },
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
        {t("qualityIndicators")}
      </h3>
      {metrics.map((m) => (
        <div key={m.label}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-300">{m.label}</span>
            <span className="font-mono text-gray-500">
              {m.value != null ? `${Math.round(m.value * 100)}%` : "—"}
            </span>
          </div>
          <Bar value={m.value ?? 0} color={m.color} />
        </div>
      ))}
    </div>
  );
}
