import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col gap-space-sm py-space-xl">
      <h1 className="text-headline-lg font-bold text-primary">Nie znaleziono strony</h1>
      <p className="text-body-lg text-on-surface-variant">Ta strona nie istnieje albo została przeniesiona.</p>
      <p>
        <Link href="/" className="text-body-lg font-bold text-primary underline">
          Wróć do strony głównej
        </Link>
      </p>
    </div>
  );
}
