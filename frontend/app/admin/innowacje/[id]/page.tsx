import type { Metadata } from "next";
import { InnovationStatsView } from "@/components/admin/InnovationStatsView";

export const metadata: Metadata = { title: "Statystyki innowacji" };

type Props = { params: Promise<{ id: string }> };

export default async function AdminInnovationPage({ params }: Props) {
  return <InnovationStatsView id={decodeURIComponent((await params).id)} />;
}
