"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { api, type Vote } from "@/lib/api";

export default function VotesPage() {
  const t = useTranslations("votes");
  const locale = useLocale();
  const [votes, setVotes] = useState<Vote[]>([]);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    const params: Record<string, string> = {};
    if (filter) params.status = filter;
    api.listVotes(params).then(setVotes).catch(console.error);
  }, [filter]);

  function getTitle(vote: Vote): string {
    const key = `title_${locale}` as keyof Vote;
    return (vote[key] as string) || vote.title_de || vote.title_fr || "Untitled";
  }

  return (
    <div>
      <h1 className="text-2xl font-serif font-bold mb-6">{t("title")}</h1>

      <div className="flex gap-2 mb-6">
        {["", "upcoming", "active", "completed"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`badge cursor-pointer ${s === filter ? "bg-signal-blue text-white" : "bg-gray-100 dark:bg-gray-800"}`}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {votes.map((vote) => (
          <div key={vote.id} className="card">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`badge ${
                    vote.status === "upcoming" ? "bg-blue-100 text-blue-800" :
                    vote.status === "active" ? "bg-green-100 text-green-800" :
                    "bg-gray-100 text-gray-800"
                  }`}>
                    {vote.status}
                  </span>
                  <span className="badge bg-gray-100 dark:bg-gray-800 text-gray-600">
                    {vote.level}
                  </span>
                  {vote.canton && (
                    <span className="badge bg-gray-100 dark:bg-gray-800 text-gray-600">
                      {vote.canton}
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-serif font-semibold">{getTitle(vote)}</h3>
              </div>
              {vote.vote_date && (
                <time className="text-sm text-gray-500 whitespace-nowrap">
                  {new Date(vote.vote_date).toLocaleDateString(locale)}
                </time>
              )}
            </div>

            {vote.official_url && (
              <a
                href={vote.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-signal-blue hover:underline mt-2 block"
              >
                Official link
              </a>
            )}
          </div>
        ))}

        {votes.length === 0 && (
          <p className="text-center text-gray-500 py-12">No votes found.</p>
        )}
      </div>
    </div>
  );
}
