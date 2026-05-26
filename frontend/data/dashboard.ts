import { Activity, AlertTriangle, Boxes, CheckCircle2 } from "lucide-react";

import type {
  ActiveProductionTask,
  AlertItem,
  InventoryCategory,
  KpiMetric,
  LowStockItem,
  ProductionPoint,
  RecentActivity,
} from "@/types/dashboard";

export const kpiMetrics: KpiMetric[] = [
  {
    label: "Total Inventory Value",
    value: "₹48,75,230",
    trend: "12.5% vs yesterday",
    trendDirection: "up",
    icon: Boxes,
    sparkline: [{ value: 28 }, { value: 34 }, { value: 31 }, { value: 42 }, { value: 47 }, { value: 54 }],
  },
  {
    label: "Low Stock Items",
    value: "18",
    trend: "Needs Attention",
    trendDirection: "up",
    icon: AlertTriangle,
    sparkline: [{ value: 42 }, { value: 38 }, { value: 34 }, { value: 27 }, { value: 22 }, { value: 18 }],
  },
  {
    label: "Active Production",
    value: "32",
    trend: "12 In Progress",
    trendDirection: "up",
    icon: Activity,
    sparkline: [{ value: 22 }, { value: 25 }, { value: 31 }, { value: 35 }, { value: 39 }, { value: 42 }],
  },
  {
    label: "Completed Today",
    value: "15",
    trend: "20% vs yesterday",
    trendDirection: "up",
    icon: CheckCircle2,
    sparkline: [{ value: 120 }, { value: 168 }, { value: 206 }, { value: 244 }, { value: 281 }, { value: 316 }],
  },
];

export const inventoryCategories: InventoryCategory[] = [
  { name: "Raw Materials", value: 50.7, color: "#19C93B" },
  { name: "Components", value: 30.9, color: "#B6E500" },
  { name: "Sub-Assemblies", value: 10.0, color: "#2563EB" },
  { name: "Finished Goods", value: 6.1, color: "#7C3AED" },
  { name: "Others", value: 2.3, color: "#AAB2C0" },
];

export const productionSeries: ProductionPoint[] = [
  { shift: "Mon", planned: 36, completed: 18 },
  { shift: "Tue", planned: 52, completed: 34 },
  { shift: "Wed", planned: 46, completed: 24 },
  { shift: "Thu", planned: 76, completed: 42 },
  { shift: "Fri", planned: 94, completed: 64 },
  { shift: "Sat", planned: 73, completed: 48 },
];

export const alerts: AlertItem[] = [
  {
    title: "Low stock: Brake Pad Kit",
    description: "Current: 5 | Minimum: 20",
    type: "low_stock",
    time: "2m ago",
  },
  {
    title: "Production delay in Line 2",
    description: "Steering Assembly",
    type: "delay",
    time: "15m ago",
  },
  {
    title: "Low stock: Oil Seal",
    description: "Current: 8 | Minimum: 25",
    type: "low_stock",
    time: "1h ago",
  },
  {
    title: "Maintenance due: CNC-02",
    description: "VMC Machine",
    type: "maintenance",
    time: "2h ago",
  },
];

export const lowStockItems: LowStockItem[] = [
  { itemName: "Brake Pad Kit", sku: "BP-001", currentStock: 5, minimumStock: 20, status: "Low" },
  { itemName: "Oil Seal", sku: "OS-002", currentStock: 8, minimumStock: 25, status: "Low" },
  { itemName: "Ball Bearing 6203", sku: "BB-6203", currentStock: 12, minimumStock: 30, status: "Low" },
  { itemName: "Clutch Plate", sku: "CP-004", currentStock: 7, minimumStock: 15, status: "Low" },
  { itemName: "Air Filter", sku: "AF-005", currentStock: 10, minimumStock: 20, status: "Low" },
];

export const activeTasks: ActiveProductionTask[] = [
  { taskName: "Steering Assembly", line: "Line 1", progress: 65, assignedWorker: "Ravi Kumar", status: "Running" },
  { taskName: "Brake Assembly", line: "Line 2", progress: 40, assignedWorker: "Neha Singh", status: "Running" },
  { taskName: "Clutch Assembly", line: "Line 1", progress: 75, assignedWorker: "Aman Verma", status: "Running" },
  { taskName: "Gear Box Assembly", line: "Line 3", progress: 10, assignedWorker: "Iqbal Khan", status: "Queued" },
  { taskName: "Engine Mount", line: "Line 2", progress: 30, assignedWorker: "Priya Nair", status: "Running" },
];

export const recentActivities: RecentActivity[] = [
  {
    title: "New stock added",
    description: "Brake Pad Kit",
    time: "10:30 AM",
    type: "inventory",
  },
  {
    title: "Work order created",
    description: "WO-1258",
    time: "09:45 AM",
    type: "task",
  },
  {
    title: "Production completed",
    description: "Clutch Assembly",
    time: "09:30 AM",
    type: "production",
  },
  {
    title: "Low stock alert",
    description: "Oil Seal",
    time: "09:15 AM",
    type: "alert",
  },
  {
    title: "Task updated",
    description: "Steering Assembly",
    time: "09:00 AM",
    type: "task",
  },
];

export const outputProgress = {
  percentage: 78,
  target: 1600,
  achieved: 1250,
  remaining: 350,
};
