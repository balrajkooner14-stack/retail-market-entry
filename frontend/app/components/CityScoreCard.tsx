import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CityScore } from "@/app/lib/types";

export function CityScoreCard({ city, insight }: { city: CityScore; insight: string }) {
  return (
    <Card className="border-2 border-[#0ca30c] bg-[#eaf7ec]">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-[#0D1B2A]">
            #{city.rank} {city.city}, {city.state}
          </CardTitle>
          <Badge className="bg-[#0ca30c] text-white">{city.composite_score.toFixed(2)} / 5.0</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-[#52514E]">{insight}</p>
      </CardContent>
    </Card>
  );
}
