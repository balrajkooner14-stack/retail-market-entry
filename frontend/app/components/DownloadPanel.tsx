import { Card, CardContent } from "@/components/ui/card";
import type { DownloadsResponse } from "@/app/lib/types";

const ITEMS: { key: keyof DownloadsResponse; label: string; icon: string }[] = [
  { key: "deck_pdf", label: "Download Full Deck (PDF)", icon: "📥" },
  { key: "deck_pptx", label: "Download Full Deck (PowerPoint)", icon: "📊" },
  { key: "excel_model", label: "Download Excel Model", icon: "📈" },
  { key: "memo_pdf", label: "Download Recommendation Memo", icon: "📄" },
];

export function DownloadPanel({ downloads }: { downloads: DownloadsResponse }) {
  const available = ITEMS.filter((item) => downloads[item.key]);

  return (
    <Card>
      <CardContent className="py-6">
        <div className="grid sm:grid-cols-2 gap-3">
          {available.map((item) => (
            <a
              key={item.key}
              href={downloads[item.key]}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-3 rounded-md border border-[#e1e0d9] hover:border-[#0D1B2A] hover:bg-[#f9f9f7] transition-colors text-sm font-medium text-[#0D1B2A]"
            >
              <span>{item.icon}</span> {item.label}
            </a>
          ))}
        </div>
        {available.length === 0 && (
          <p className="text-sm text-[#898781]">Deliverable files not yet generated.</p>
        )}
      </CardContent>
    </Card>
  );
}
