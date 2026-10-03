import type { Metadata } from "next";
import { AdminPanel } from "@/components/admin/AdminPanel";

export const metadata: Metadata = {
  title: "Panel administratora",
  robots: { index: false },
};

// login is off for the demo; the backend honours ADMIN_AUTH_DISABLED only in debug
export default function AdminPage() {
  return <AdminPanel />;
}
