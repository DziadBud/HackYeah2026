import type { Metadata } from "next";
import { InnovationEdit } from "@/components/admin/InnovationForm";

export const metadata: Metadata = { title: "Edytuj innowację" };

type Props = { params: Promise<{ id: string }> };

export default async function AdminEditInnovationPage({ params }: Props) {
  return <InnovationEdit id={decodeURIComponent((await params).id)} />;
}
