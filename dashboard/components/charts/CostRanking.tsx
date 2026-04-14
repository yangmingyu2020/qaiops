import type { TopCostItem } from "@/lib/api";

interface CostRankingProps {
  data: TopCostItem[];
}

function formatCost(cost: number): string {
  if (cost < 0.001) return `$${cost.toFixed(6)}`;
  return `$${cost.toFixed(4)}`;
}

const toolColors: Record<string, string> = {
  claude: "bg-orange-100 text-orange-700",
  gemini: "bg-blue-100 text-blue-700",
  gpt: "bg-green-100 text-green-700",
};

export default function CostRanking({ data }: CostRankingProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">Top Expensive Requests</h3>
      {data.length === 0 ? (
        <div className="text-gray-400 text-sm text-center py-8">No data available</div>
      ) : (
        <div className="space-y-3">
          {data.map((item, index) => (
            <div
              key={item.id}
              className="flex items-start gap-3 text-sm"
            >
              <span className="text-gray-400 font-mono text-xs mt-0.5 w-4">
                {index + 1}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${
                      toolColors[item.tool_name] || "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {item.tool_name}
                  </span>
                  {item.model_name && (
                    <span className="text-xs text-gray-400">{item.model_name}</span>
                  )}
                </div>
                <p className="text-gray-600 truncate">{item.prompt_text}</p>
              </div>
              <div className="text-right whitespace-nowrap">
                <p className="font-medium text-gray-900">{formatCost(item.total_cost)}</p>
                <p className="text-xs text-gray-400">
                  {(item.input_tokens + item.output_tokens).toLocaleString()} tokens
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
