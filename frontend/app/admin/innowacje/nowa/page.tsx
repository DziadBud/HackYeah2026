import type { Metadata } from "next";
import { InnovationForm } from "@/components/admin/InnovationForm";

export const metadata: Metadata = { title: "Dodaj innowację" };

export default function AdminNewInnovationPage() {
  return <InnovationForm />;
}
