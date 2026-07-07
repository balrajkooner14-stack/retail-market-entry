"use client";

import { Bar, BarChart, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/app/lib/types";
import type { FinancialCity } from "@/app/lib/types";

export function FinancialTable({ data }: { data: FinancialCity }) {
  const chartData = [
    { year: "Year 1", ebitda: data.y1_ebitda },
    { year: "Year 2", ebitda: data.y2_ebitda },
    { year: "Year 3", ebitda: data.y3_ebitda },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-[#0D1B2A]">{data.city}</CardTitle>
          <Badge variant={data.payback_months ? "default" : "secondary"}>
            {data.payback_months ? `Payback: ${Math.round(data.payback_months)} mo` : "Beyond 3yr horizon"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-2 text-sm mb-4">
          <div>
            <div className="text-[#898781]">Y1 EBITDA</div>
            <div className={data.y1_ebitda >= 0 ? "text-[#006300] font-semibold" : "text-[#d03b3b] font-semibold"}>
              {formatCurrency(data.y1_ebitda)}
            </div>
          </div>
          <div>
            <div className="text-[#898781]">Y2 EBITDA</div>
            <div className={data.y2_ebitda >= 0 ? "text-[#006300] font-semibold" : "text-[#d03b3b] font-semibold"}>
              {formatCurrency(data.y2_ebitda)}
            </div>
          </div>
          <div>
            <div className="text-[#898781]">Y3 EBITDA</div>
            <div className={data.y3_ebitda >= 0 ? "text-[#006300] font-semibold" : "text-[#d03b3b] font-semibold"}>
              {formatCurrency(data.y3_ebitda)}
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={140}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e1e0d9" vertical={false} />
            <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#52514E" }} />
            <YAxis tick={{ fontSize: 10, fill: "#898781" }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(v) => (typeof v === "number" ? formatCurrency(v) : v)} />
            <Bar dataKey="ebitda" fill="#0ca30c" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 gap-4 text-sm mt-4 pt-4 border-t border-[#e1e0d9]">
          <div>
            <div className="text-[#898781]">NPV (Base, 10%)</div>
            <div className="font-semibold">{formatCurrency(data.npv_base)}</div>
          </div>
          <div>
            <div className="text-[#898781]">NPV (Risk-Adjusted, 12%)</div>
            <div className="font-semibold">{formatCurrency(data.npv_risk_adjusted)}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
