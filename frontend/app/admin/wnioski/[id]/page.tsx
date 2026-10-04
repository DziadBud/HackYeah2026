import type { Metadata } from "next";
import { GrantApplicationView } from "@/components/admin/GrantApplicationView";

export const metadata: Metadata = { title: "Wniosek o grant" };

type Props = { params: Promise<{ id: string }> };

export default async function AdminGrantApplicationPage({ params }: Props) {
  return <GrantApplicationView id={decodeURIComponent((await params).id)} />;
}
