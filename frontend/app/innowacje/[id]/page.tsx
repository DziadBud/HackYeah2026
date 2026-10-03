import type { Metadata } from "next";
import { InnovationDetail } from "@/components/innovation/InnovationDetail";

// fetched in the browser like every other api call (NEXT_PUBLIC_API_URL is the browser's view of the api)
export const metadata: Metadata = { title: "Innowacja" };

type Props = { params: Promise<{ id: string }> };

export default async function InnovationPage({ params }: Props) {
  return <InnovationDetail id={decodeURIComponent((await params).id)} />;
}
