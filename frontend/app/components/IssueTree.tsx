import { Card, CardContent } from "@/components/ui/card";
import type { MethodologyResponse } from "@/app/lib/types";

export function IssueTree({ issueTree }: { issueTree: MethodologyResponse["issue_tree"] }) {
  return (
    <div className="space-y-4">
      <Card className="bg-[#0D1B2A] text-white">
        <CardContent className="py-4">
          <p className="text-sm text-[#F9A825] font-semibold mb-1">Central Question</p>
          <p className="text-base">{issueTree.central_question}</p>
        </CardContent>
      </Card>
      <div className="grid md:grid-cols-3 gap-4">
        {issueTree.branches.map((branch) => (
          <Card key={branch.name} className="border-[#e1e0d9]">
            <CardContent className="py-4">
              <p className="font-semibold text-[#0D1B2A] mb-2">{branch.name}</p>
              <ul className="space-y-1 text-sm text-[#52514E] list-disc list-inside">
                {branch.sub_questions.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
