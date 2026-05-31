"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = window.localStorage.getItem("naptech_access_token");
    router.replace(token ? "/dashboard" : "/login");
  }, [router]);

  return (
    <main className="grid min-h-screen place-items-center bg-[#F7F9FB] text-sm font-medium text-slate-500">
      Opening Naptech Factory OS...
    </main>
  );
}
