"use client";

import { AlertTriangle, Bell, CheckCircle2, ClipboardList, Loader2 } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { Badge, Card, PageHeader } from "@/components/ui";
import { getNotifications } from "@/lib/api";
import { formatDateTime, titleCase } from "@/lib/format";
import type { Notification } from "@/lib/types";

const icons: Record<Notification["type"], ReactNode> = {
  low_stock: <AlertTriangle size={20} />,
  production_delay: <ClipboardList size={20} />,
  task_update: <CheckCircle2 size={20} />,
};

const tones: Record<Notification["type"], "warning" | "danger" | "info"> = {
  low_stock: "warning",
  production_delay: "danger",
  task_update: "info",
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    void loadNotifications();
  }, []);

  async function loadNotifications() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getNotifications();
      setNotifications(response);
    } catch {
      setError("Unable to load notifications. Please login again and retry.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <DashboardShell>
      <PageHeader
        description="Operational alerts for low stock, production delays, and task status changes."
        title="Notifications"
      />

      <Card>
        <div className="mb-4 flex items-center gap-2">
          <Bell size={18} className="text-cyan-700" />
          <h2 className="text-base font-semibold text-slate-950">Alerts Panel</h2>
        </div>

        {error ? <p className="mb-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">{error}</p> : null}

        {isLoading ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="animate-spin" size={16} />
            Loading notifications...
          </div>
        ) : notifications.length ? (
          <div className="space-y-3">
            {notifications.map((notification) => (
              <div
                className="flex flex-col gap-3 rounded-md border border-border p-4 md:flex-row md:items-center md:justify-between"
                key={notification.id}
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700">
                    {icons[notification.type]}
                  </div>
                  <div>
                    <p className="font-medium text-slate-950">{notification.message}</p>
                    <p className="text-sm text-muted-foreground">{formatDateTime(notification.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={tones[notification.type]}>{titleCase(notification.type)}</Badge>
                  <Badge tone={notification.is_read ? "neutral" : "success"}>
                    {notification.is_read ? "Read" : "New"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-slate-50 p-5 text-sm text-slate-600">
            No operational alerts right now. New low stock, production delay, and saved production updates will appear here.
          </div>
        )}
      </Card>
    </DashboardShell>
  );
}
