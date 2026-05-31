"use client";

import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type LoginInputProps = {
  autoComplete?: string;
  defaultValue?: string;
  icon: LucideIcon;
  label: string;
  name: string;
  placeholder: string;
  rightSlot?: ReactNode;
  type?: string;
};

export function LoginInput({
  autoComplete,
  defaultValue,
  icon: Icon,
  label,
  name,
  placeholder,
  rightSlot,
  type = "text",
}: Readonly<LoginInputProps>) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-[#111827]">{label}</span>
      <span className="flex h-12 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 shadow-[0_8px_30px_rgba(2,11,20,0.05)] transition focus-within:border-[#19C93B]/50 focus-within:ring-4 focus-within:ring-[#19C93B]/12">
        <Icon className="shrink-0 text-[#19C93B]" size={18} />
        <input
          autoComplete={autoComplete}
          className="w-full bg-transparent text-[15px] text-[#111827] outline-none placeholder:text-slate-400"
          defaultValue={defaultValue}
          name={name}
          placeholder={placeholder}
          type={type}
        />
        {rightSlot}
      </span>
    </label>
  );
}
