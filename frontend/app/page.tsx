"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CityScoreCard } from "@/app/components/CityScoreCard";
import { RadarChartPanel } from "@/app/components/RadarChartPanel";
import { FinancialTable } from "@/app/components/FinancialTable";
import { IssueTree } from "@/app/components/IssueTree";
import { DownloadPanel } from "@/app/components/DownloadPanel";
import { DIMENSION_LABELS } from "@/app/lib/types";
import type {
  ScoresResponse,
  FinancialResponse,
  MethodologyResponse,
  DownloadsResponse,
} from "@/app/lib/types";

const CITY_INSIGHTS: Record<string, string> = {
  Indianapolis:
    "Cheapest lease rate and least competitive density of any candidate, but slower population growth means its financial case needs a longer runway than our 3-year model window — recommended as a single pilot store.",
  Charlotte:
    "Sits at Meridian's own East Coast distribution hub (zero logistics cost) with the strongest housing fundamentals of the five candidates — the only recommended market that clears payback within 3 years.",
};

function scoreColor(score: number): string {
  if (score >= 4) return "#0ca30c";
  if (score >= 3) return "#eda100";
  return "#d03b3b";
}

export default function Home() {
  const [scores, setScores] = useState<ScoresResponse | null>(null);
  const [financial, setFinancial] = useState<FinancialResponse | null>(null);
  const [methodology, setMethodology] = useState<MethodologyResponse | null>(null);
  const [downloads, setDownloads] = useState<DownloadsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/scores").then((r) => r.json()),
      fetch("/api/financial").then((r) => r.json()),
      fetch("/api/methodology").then((r) => r.json()),
      fetch("/api/downloads").then((r) => r.json()),
    ])
      .then(([s, f, m, d]) => {
        setScores(s);
        setFinancial(f);
        setMethodology(m);
        setDownloads(d);
      })
      .catch(() => setError("Could not reach the API. Is the FastAPI backend running on port 8000?"));
  }, []);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-24 text-center text-[#d03b3b]">{error}</div>
    );
  }

  if (!scores || !financial || !methodology || !downloads) {
    return <div className="max-w-2xl mx-auto px-6 py-24 text-center text-[#898781]">Loading analysis…</div>;
  }

  const recommendedCities = scores.cities.filter((c) => c.recommended);
  const compositeChartData = [...scores.cities]
    .sort((a, b) => b.composite_score - a.composite_score)
    .map((c) => ({ name: `${c.city}, ${c.state}`, score: c.composite_score, recommended: c.recommended }));

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 space-y-20">
      {/* Hero */}
      <section className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-[#0D1B2A]">
          Which Two Markets Should Meridian Home Enter Next?
        </h1>
        <p className="text-lg text-[#52514E] max-w-2xl mx-auto">
          A McKinsey-style market entry analysis across 5 US metros using 7 data-driven scoring
          dimensions
        </p>
        <div className="grid sm:grid-cols-2 gap-4 max-w-3xl mx-auto pt-6">
          {recommendedCities.map((city) => (
            <CityScoreCard key={city.city} city={city} insight={CITY_INSIGHTS[city.city] ?? ""} />
          ))}
        </div>
      </section>

      {/* Composite score chart */}
      <section id="analysis" className="space-y-4">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">Overall Market Attractiveness Ranking</h2>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={compositeChartData} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e1e0d9" horizontal={false} />
            <XAxis type="number" domain={[0, 5]} tick={{ fill: "#52514E", fontSize: 12 }} />
            <YAxis type="category" dataKey="name" width={110} tick={{ fill: "#0b0b0b", fontSize: 13 }} />
            <Tooltip formatter={(v) => (typeof v === "number" ? v.toFixed(2) : v)} />
            <Bar dataKey="score" radius={[0, 4, 4, 0]}>
              {compositeChartData.map((entry) => (
                <Cell key={entry.name} fill={entry.recommended ? "#0ca30c" : "#898781"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <p className="text-sm text-[#898781]">{scores.sensitivity}</p>
      </section>

      {/* Scoring matrix table */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">7-Dimension Scoring Matrix</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>City</TableHead>
                {DIMENSION_LABELS.map((label) => (
                  <TableHead key={label} className="text-center">
                    {label}
                  </TableHead>
                ))}
                <TableHead className="text-center font-bold">Composite</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...scores.cities]
                .sort((a, b) => a.rank - b.rank)
                .map((city) => (
                  <TableRow key={city.city} className={city.recommended ? "bg-[#eaf7ec]" : ""}>
                    <TableCell className="font-medium">
                      {city.city}, {city.state}
                    </TableCell>
                    {[1, 2, 3, 4, 5, 6, 7].map((i) => {
                      const score = city[`dim${i}_score` as keyof typeof city] as number;
                      return (
                        <TableCell key={i} className="text-center" style={{ color: scoreColor(score) }}>
                          {score.toFixed(1)}
                        </TableCell>
                      );
                    })}
                    <TableCell className="text-center font-bold">
                      {city.composite_score.toFixed(2)}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* Radar chart */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">Multi-Dimensional Market Profile</h2>
        <RadarChartPanel cities={scores.cities} />
      </section>

      {/* Financial model */}
      <section id="financial" className="space-y-4">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">3-Year Financial Projection</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {financial.cities.map((city) => (
            <FinancialTable key={city.city} data={city} />
          ))}
        </div>
      </section>

      {/* Methodology */}
      <section id="methodology" className="space-y-4">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">Analytical Framework</h2>
        <p className="text-sm text-[#52514E] max-w-3xl">
          Structured using the McKinsey Pyramid Principle: a MECE issue tree decomposes the central
          question into three branches, each tested with weighted, sourced data before reaching a
          recommendation.
        </p>
        <IssueTree issueTree={methodology.issue_tree} />
      </section>

      {/* Downloads */}
      <section id="downloads" className="space-y-4 pb-12">
        <h2 className="text-2xl font-semibold text-[#0D1B2A]">Downloads</h2>
        <DownloadPanel downloads={downloads} />
        <p className="text-sm text-[#898781]">
          <a
            href="https://github.com/balrajkooner14-stack/retail-market-entry"
            className="underline hover:text-[#0D1B2A]"
            target="_blank"
            rel="noopener noreferrer"
          >
            View source on GitHub
          </a>
        </p>
      </section>
    </div>
  );
}
