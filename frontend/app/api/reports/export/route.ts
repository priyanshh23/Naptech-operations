import { NextResponse } from "next/server";

import { activeTasks, alerts, lowStockItems, outputProgress } from "@/data/dashboard";

export function GET() {
  const rows = [
    ["Section", "Metric", "Value"],
    ["Production", "Target", String(outputProgress.target)],
    ["Production", "Achieved", String(outputProgress.achieved)],
    ["Production", "Remaining", String(outputProgress.remaining)],
    ...lowStockItems.map((item) => ["Low Stock", `${item.itemName} (${item.sku})`, String(item.currentStock)]),
    ...activeTasks.map((task) => ["Task", `${task.taskName} - ${task.line}`, `${task.progress}% ${task.status}`]),
    ...alerts.map((alert) => ["Alert", alert.title, alert.description]),
  ];

  const csv = rows.map((row) => row.map((cell) => `"${cell.replaceAll('"', '""')}"`).join(",")).join("\n");

  return new NextResponse(csv, {
    headers: {
      "content-disposition": "attachment; filename=naptech-factory-report.csv",
      "content-type": "text/csv; charset=utf-8",
    },
  });
}

