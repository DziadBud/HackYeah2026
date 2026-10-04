import type { Metadata } from "next";
import { GrantApplicationList } from "@/components/admin/GrantApplicationList";

export const metadata: Metadata = { title: "Wnioski o grant" };

export default function AdminGrantApplicationsPage() {
  return <GrantApplicationList />;
}
