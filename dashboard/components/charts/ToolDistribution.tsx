"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { DailyStats } from "@/lib/api";

interface ToolDistributionProps {
  data: DailyStats[];
}

const COLORS = ["#f97316", "#3b82f6", "#22c55e", "#a855f7", "#ef4444"];

export default function ToolDistribution({ data }: ToolDistributionProps) {
  // Aggregate by tool
  const byTool = new Map<string, number>();
  for (const item of data) {
    byTool.set(item.tool_name, (byTool.get(item.tool_name) || 0) + item.total_requests);
  }

  const chartData = Array.from(byTool.entries()).map(([name, value]) => ({
    name,
    value,
  }));

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Tool Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">Tool Distribution</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            dataKey="value"
            paddingAngle={2}
          >
            {chartData.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => [value, "Requests"]} />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
