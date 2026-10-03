import type { Metadata } from "next";
import { AdminPanel } from "@/components/admin/AdminPanel";

export const metadata: Metadata = { title: "Zgłoszenia, pomysły i raporty" };

export default function AdminReportsPage() {
  return <AdminPanel />;
}
