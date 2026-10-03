import type { Metadata } from "next";
import { AdminGate } from "@/components/admin/AdminGate";

export const metadata: Metadata = {
  title: { default: "Panel administratora", template: "%s – Panel administratora" },
  robots: { index: false },
};

// login via /admin/auth/*; with DEBUG=true and ADMIN_AUTH_DISABLED=true the backend skips it (demo)
export default function AdminLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex flex-col gap-space-lg py-space-md">
      <AdminGate>{children}</AdminGate>
    </div>
  );
}
