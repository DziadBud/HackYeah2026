import type { Metadata } from "next";
import { TestSignupList } from "@/components/admin/TestSignupList";

export const metadata: Metadata = { title: "Zgłoszenia do testów" };

export default function AdminTestSignupsPage() {
  return <TestSignupList />;
}
