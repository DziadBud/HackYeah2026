import { A11yToolbar } from "@/components/A11yToolbar";
import { SiteHeader } from "@/components/SiteHeader";

// shared chrome: a11y strip + site header, used by every public page via layout
export function TopBar() {
  return (
    <>
      <A11yToolbar />
      <SiteHeader />
    </>
  );
}
