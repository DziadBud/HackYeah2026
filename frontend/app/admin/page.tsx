// admin panel skeleton. real screens sit behind JWT auth (see
// documentation/backend/architecture.md §5); this is just a placeholder shell.
export default function AdminPage() {
  const sections = [
    { title: "Innowacje", desc: "CRUD + publikacja wpisów z bazy" },
    { title: "Import", desc: "ingest JSON / CSV / PDF, podgląd zadań" },
    { title: "Skrzynka", desc: "nowe pomysły oraz krytyczne zgłoszenia" },
    { title: "Zgłoszenia i pomysły", desc: "odpowiedzi, zmiana statusu" },
    { title: "Raporty", desc: "trendy, krytyczne, gminy, luki + eksport CSV" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <section className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">Panel administratora</h1>
        <p className="text-sm text-black/60 dark:text-white/60">
          Szkielet. Docelowo dostępny po zalogowaniu (JWT, rola admin).
        </p>
      </section>

      <div className="grid gap-3 sm:grid-cols-2">
        {sections.map((s) => (
          <div
            key={s.title}
            className="rounded-lg border border-black/10 p-4 dark:border-white/10"
          >
            <h2 className="font-medium">{s.title}</h2>
            <p className="mt-1 text-sm text-black/60 dark:text-white/60">{s.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
