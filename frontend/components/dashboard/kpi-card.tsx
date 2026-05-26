"use client";

import { AlertTriangle, ArrowDownRight, ArrowUpRight } from "lucide-react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
} from "recharts";

import { DashboardCard } from "@/components/dashboard/dashboard-card";
import type { KpiMetric } from "@/types/dashboard";

export function KpiCard({ metric, index }: Readonly<{ metric: KpiMetric; index: number }>) {
  const Icon = metric.icon;
  const TrendIcon = metric.label === "Low Stock Items" ? AlertTriangle : metric.trendDirection === "up" ? ArrowUpRight : ArrowDownRight;
  const accent =
    metric.label === "Low Stock Items"
      ? { text: "text-amber-600", bg: "bg-amber-50", stroke: "#F59E0B" }
      : metric.label === "Active Production"
        ? { text: "text-blue-600", bg: "bg-blue-50", stroke: "#2563EB" }
        : metric.label === "Completed Today"
          ? { text: "text-violet-600", bg: "bg-violet-50", stroke: "#7C3AED" }
          : { text: "text-[#19C93B]", bg: "bg-[#19C93B]/10", stroke: "#19C93B" };

  return (
    <DashboardCard className="p-4" delay={index * 0.05}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[#6B7280]">{metric.label}</p>
          <p className="mt-2 text-2xl font-semibold tracking-normal text-[#111827]">{metric.value}</p>
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-full ${accent.bg} ${accent.text}`}>
          <Icon size={19} />
        </div>
      </div>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold ${accent.bg} ${accent.text}`}>
          <TrendIcon size={12} />
          {metric.trend}
        </div>
        <div className="h-10 w-24">
          <ResponsiveContainer height="100%" width="100%">
            <AreaChart data={metric.sparkline}>
              <defs>
                <linearGradient id={`kpiGradient-${index}`} x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor={accent.stroke} stopOpacity={0.45} />
                  <stop offset="95%" stopColor={accent.stroke} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                dataKey="value"
                fill={`url(#kpiGradient-${index})`}
                stroke={accent.stroke}
                strokeWidth={2}
                type="monotone"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </DashboardCard>
  );
}
