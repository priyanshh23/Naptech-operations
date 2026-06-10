import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Card({
  children,
  className,
}: Readonly<{
  children: ReactNode;
  className?: string;
}>) {
  return (
    <section className={cn("rounded-lg border border-border bg-white p-5 shadow-panel", className)}>
      {children}
    </section>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: Readonly<{
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
}>) {
  const toneClass = {
    neutral: "bg-slate-100 text-slate-700",
    success: "bg-emerald-50 text-emerald-700",
    warning: "bg-amber-50 text-amber-700",
    danger: "bg-red-50 text-red-700",
    info: "bg-cyan-50 text-cyan-700",
  }[tone];

  return (
    <span className={cn("inline-flex rounded-md px-2 py-1 text-xs font-semibold", toneClass)}>
      {children}
    </span>
  );
}

export function PageHeader({
  title,
  description,
  action,
}: Readonly<{
  title: string;
  description: string;
  action?: ReactNode;
}>) {
  return (
    <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div className="min-w-0">
        <h1 className="break-words text-2xl font-semibold tracking-normal text-slate-950">{title}</h1>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function Button({
  children,
  className,
  type = "button",
  ...props
}: Readonly<
  {
    children: ReactNode;
    className?: string;
    type?: "button" | "submit";
  } & ButtonHTMLAttributes<HTMLButtonElement>
>) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90",
        className,
      )}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}

export function MobileRecordCard({
  actions,
  badge,
  rows,
  subtitle,
  title,
}: Readonly<{
  actions?: ReactNode;
  badge?: ReactNode;
  rows: Array<{ label: string; value: ReactNode }>;
  subtitle?: ReactNode;
  title: ReactNode;
}>) {
  return (
    <article className="rounded-2xl border border-border bg-white p-4 shadow-sm dark:bg-white/[0.04]">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="break-words text-sm font-semibold text-slate-950 dark:text-white">{title}</h3>
          {subtitle ? <p className="mt-1 break-words text-xs text-slate-500 dark:text-slate-400">{subtitle}</p> : null}
        </div>
        {badge ? <div className="shrink-0">{badge}</div> : null}
      </div>
      <dl className="mt-4 grid grid-cols-2 gap-2">
        {rows.map((row) => (
          <div className="min-w-0 rounded-xl bg-slate-50 px-3 py-2 dark:bg-white/5" key={row.label}>
            <dt className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">{row.label}</dt>
            <dd className="mt-1 break-words text-sm font-semibold text-slate-800 dark:text-slate-100">{row.value}</dd>
          </div>
        ))}
      </dl>
      {actions ? <div className="mt-4 flex flex-wrap gap-2 border-t border-border pt-3">{actions}</div> : null}
    </article>
  );
}
