import type { Metadata } from "next";
import { InnovationList } from "@/components/admin/InnovationList";

export const metadata: Metadata = { title: "Innowacje i statystyki" };

export default function AdminPage() {
  return <InnovationList />;
}
