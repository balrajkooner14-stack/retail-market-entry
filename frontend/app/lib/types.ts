export interface CityScore {
  city: string;
  state: string;
  composite_score: number;
  rank: number;
  recommended: boolean;
  dim1_score: number;
  dim2_score: number;
  dim3_score: number;
  dim4_score: number;
  dim5_score: number;
  dim6_score: number;
  dim7_score: number;
  dim1_raw: string;
  dim2_raw: string;
  dim3_raw: string;
  dim4_raw: string;
  dim5_raw: string;
  dim6_raw: string;
  dim7_raw: string;
}

export interface ScoresResponse {
  cities: CityScore[];
  recommendation: string;
  sensitivity: string;
}

export interface FinancialCity {
  city: string;
  y1_revenue: number;
  y2_revenue: number;
  y3_revenue: number;
  y1_ebitda: number;
  y2_ebitda: number;
  y3_ebitda: number;
  payback_months: number | null;
  npv_base: number;
  npv_risk_adjusted: number;
  scenario_pessimistic_npv: number;
  scenario_optimistic_npv: number;
}

export interface FinancialResponse {
  cities: FinancialCity[];
}

export interface MethodologyResponse {
  issue_tree: {
    central_question: string;
    branches: { name: string; sub_questions: string[] }[];
  };
  dimensions: { name: string; weight: number; source: string }[];
}

export interface DownloadsResponse {
  deck_pptx?: string;
  deck_pdf?: string;
  excel_model?: string;
  memo_pdf?: string;
}

export const DIMENSION_LABELS = [
  "Population & Growth",
  "Income & Furnishing Spend",
  "Homeownership & Housing",
  "Competitive Saturation",
  "Retail Lease Cost",
  "Labor Cost",
  "Logistics Proximity",
];

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
