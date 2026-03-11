"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { api, type Entity, type IO, type EntityRelation } from "@/lib/api";
import { IOCard } from "@/components/IOCard";

export default function EntityProfilePage({ params }: { params: { id: string } }) {
  const t = useTranslations("io");
  const [entity, setEntity] = useState<Entity | null>(null);
  const [ios, setIOs] = useState<IO[]>([]);
  const [relations, setRelations] = useState<EntityRelation[]>([]);

  useEffect(() => {
    api.getEntity(params.id).then(setEntity).catch(console.error);
    api.getEntityIOs(params.id).then(setIOs).catch(console.error);
    api.getEntityRelations(params.id).then(setRelations).catch(console.error);
  }, [params.id]);

  if (!entity) {
    return <div className="card animate-pulse h-48" />;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* Entity header */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-signal-blue flex items-center justify-center text-white text-lg font-bold">
              {entity.canonical_name.charAt(0)}
            </div>
            <div>
              <h1 className="text-2xl font-serif font-bold">{entity.canonical_name}</h1>
              <span className="badge bg-gray-100 dark:bg-gray-800">
                {entity.entity_type.replace("_", " ")}
              </span>
            </div>
          </div>

          {entity.aliases && entity.aliases.length > 0 && (
            <div className="text-sm text-gray-500">
              Also known as: {entity.aliases.join(", ")}
            </div>
          )}

          <div className="flex gap-4 mt-4 text-sm text-gray-500">
            <span>Mentions: {entity.mention_count}</span>
            {entity.wikidata_id && (
              <a
                href={`https://www.wikidata.org/wiki/${entity.wikidata_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-signal-blue hover:underline"
              >
                Wikidata
              </a>
            )}
          </div>
        </div>

        {/* Related IOs */}
        <div>
          <h2 className="text-lg font-serif font-semibold mb-4">
            {t("relatedStories")} ({ios.length})
          </h2>
          <div className="space-y-4">
            {ios.map((io) => (
              <IOCard key={io.id} io={io} />
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar: Relations */}
      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Relations ({relations.length})
          </h3>
          <div className="space-y-2">
            {relations.map((rel) => (
              <div key={rel.id} className="card !p-3 text-sm">
                <span className="text-gray-500">{rel.relation_type.replace("_", " ")}</span>
                <span className="mx-2">→</span>
                <span className="font-medium">
                  {rel.source_entity_id === entity.id ? rel.target_entity_id : rel.source_entity_id}
                </span>
                <div className="text-xs text-gray-400 mt-1">
                  Confidence: {Math.round(rel.confidence * 100)}%
                </div>
              </div>
            ))}
            {relations.length === 0 && (
              <p className="text-sm text-gray-500">No relations found yet.</p>
            )}
          </div>
        </div>

        {/* Entity metadata */}
        {Object.keys(entity.metadata).length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Details
            </h3>
            <div className="space-y-1 text-sm">
              {Object.entries(entity.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-500">{key}</span>
                  <span className="font-mono">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
