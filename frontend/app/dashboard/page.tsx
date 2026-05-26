"use client";

import { ActivityTimeline } from "@/components/dashboard/activity-timeline";
import { AlertsPanel } from "@/components/dashboard/alerts-panel";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { InventoryOverview, ProductionOverview } from "@/components/dashboard/charts";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { ProductionOutputWidget } from "@/components/dashboard/output-widget";
import { ActiveTasksTable, LowStockTable } from "@/components/dashboard/tables";
import {
  activeTasks,
  alerts,
  inventoryCategories,
  kpiMetrics,
  lowStockItems,
  outputProgress,
  productionSeries,
  recentActivities,
} from "@/data/dashboard";

export default function DashboardPage() {
  return (
    <DashboardShell>
      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {kpiMetrics.map((metric, index) => (
          <KpiCard index={index} key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="mt-5 grid gap-5 xl:grid-cols-12">
        <InventoryOverview data={inventoryCategories} />
        <ProductionOverview data={productionSeries} />
      </section>

      <section className="mt-5 grid gap-5 xl:grid-cols-[1fr_360px]">
        <AlertsPanel alerts={alerts} />
        <ProductionOutputWidget {...outputProgress} />
      </section>

      <section className="mt-5 grid gap-5 lg:grid-cols-12">
        <LowStockTable items={lowStockItems} />
        <ActiveTasksTable tasks={activeTasks} />
      </section>

      <section className="mt-5 grid gap-5 lg:grid-cols-12">
        <ActivityTimeline items={recentActivities} />
      </section>
    </DashboardShell>
  );
}
