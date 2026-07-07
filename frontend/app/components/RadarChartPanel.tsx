"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { CityScore } from "@/app/lib/types";
import { DIMENSION_LABELS } from "@/app/lib/types";

const CITY_COLORS: Record<string, string> = {
  "Nashville, TN": "#2a78d6",
  "Austin, TX": "#1baf7a",
  "Denver, CO": "#eda100",
  "Charlotte, NC": "#008300",
  "Indianapolis, IN": "#4a3aa7",
};

export function RadarChartPanel({ cities }: { cities: CityScore[] }) {
  const data = DIMENSION_LABELS.map((label, i) => {
    const dimKey = `dim${i + 1}_score` as keyof CityScore;
    const row: Record<string, string | number> = { dimension: label };
    for (const city of cities) {
      row[`${city.city}, ${city.state}`] = city[dimKey] as number;
    }
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={480}>
      <RadarChart data={data} outerRadius="70%">
        <PolarGrid stroke="#e1e0d9" />
        <PolarAngleAxis dataKey="dimension" tick={{ fill: "#52514E", fontSize: 12 }} />
        <PolarRadiusAxis domain={[0, 5]} tick={{ fill: "#898781", fontSize: 10 }} />
        {cities.map((city) => {
          const key = `${city.city}, ${city.state}`;
          const color = CITY_COLORS[key] ?? "#898781";
          return (
            <Radar
              key={key}
              name={key}
              dataKey={key}
              stroke={color}
              fill={color}
              fillOpacity={0.08}
              strokeWidth={2}
            />
          );
        })}
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}
