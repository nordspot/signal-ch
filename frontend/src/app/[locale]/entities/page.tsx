"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { api, type Entity, type EntityListResponse } from "@/lib/api";

const ENTITY_TYPES = [
  "person", "organization", "company", "political_party",
  "government_body", "location", "law",
];

export default function EntitiesPage() {
  const t = useTranslations("nav");
  const [data, setData] = useState<EntityListResponse | null>(null);
  const [type, setType] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const params: Record<string, string> = {};
    if (type) params.entity_type = type;
    if (search) params.q = search;
    api.listEntities(params).then(setData).catch(console.error);
  }, [type, search]);

  return (
    <div>
      <h1 className="text-2xl font-serif font-bold mb-6">{t("entities")}</h1>

      <div className="flex flex-wrap gap-2 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search entities..."
          className="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-signal-dark-card text-sm"
        />
        <button
          onClick={() => setType("")}
          className={`badge cursor-pointer ${!type ? "bg-signal-blue text-white" : "bg-gray-100 dark:bg-gray-800"}`}
        >
          All
        </button>
        {ENTITY_TYPES.map((et) => (
          <button
            key={et}
            onClick={() => setType(et === type ? "" : et)}
            className={`badge cursor-pointer ${et === type ? "bg-signal-blue text-white" : "bg-gray-100 dark:bg-gray-800"}`}
          >
            {et.replace("_", " ")}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.items.map((entity) => (
          <Link key={entity.id} href={`/entity/${entity.id}`} className="card hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{entity.canonical_name}</h3>
                <span className="badge bg-gray-100 dark:bg-gray-800 text-xs mt-1">
                  {entity.entity_type.replace("_", " ")}
                </span>
              </div>
              <span className="text-sm text-gray-500 font-mono">{entity.mention_count}</span>
            </div>
            {entity.aliases && entity.aliases.length > 1 && (
              <p className="text-xs text-gray-400 mt-2 truncate">
                aka: {entity.aliases.slice(0, 3).join(", ")}
              </p>
            )}
          </Link>
        ))}
      </div>

      {data && data.items.length === 0 && (
        <p className="text-center text-gray-500 py-12">No entities found.</p>
      )}
    </div>
  );
}
