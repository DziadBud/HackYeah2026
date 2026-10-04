// ROPS Zał. 3 labels shared by the public form and the admin review
import type { ApplicantType } from "@/lib/api";

export const APPLICANT_LABELS: Record<ApplicantType, string> = {
  person: "Osoba fizyczna",
  organization: "Podmiot (organizacja)",
  informal_group: "Grupa nieformalna",
};

export const PERSON_DECL: Record<string, string> = {
  resides_in_poland: "Posiadam miejsce zamieszkania na terenie Polski",
  full_legal_capacity: "Posiadam pełną zdolność do czynności prawnych",
  no_criminal_conviction: "Nie byłem/am skazany/a prawomocnym wyrokiem za umyślne przestępstwo",
  not_excluded_public_funds: "Nie jestem wykluczony/a z otrzymania środków europejskich (art. 207 u.f.p.)",
  not_under_sanctions: "Nie podlegam wykluczeniu z powodu sankcji związanych z agresją na Ukrainę",
  no_tax_arrears: "Nie zalegam z podatkami, opłatami ani składkami",
  voluntary_participation: "Dobrowolnie deklaruję uczestnictwo w projekcie Inkubator Włączenia Społecznego 2.0",
  accepts_procedures: "Zapoznałem/am się z Procedurami i akceptuję warunki",
  data_truthful: "Dane w formularzu są zgodne z prawdą",
  not_employed_rops_innoagh: "Nie jestem zatrudniony/a w ROPS ani INNOAGH i nie łączą mnie z nimi wskazane więzi",
  no_parallel_application: "Nie aplikuję równolegle o wsparcie na ten sam pomysł w innym projekcie FERS 5.1",
  not_duplicating_existing: "Innowacja nie powiela już wdrożonych / inkubowanych rozwiązań w Polsce",
  no_fees_from_testers: "Nie będę pobierał/a opłat od osób testujących innowację",
  max_two_applications: "W ramach naboru składam nie więcej niż 2 aplikacje",
  not_implementation_character: "Innowacja nie ma charakteru wdrożeniowego",
  aware_form_shared: "Jestem świadomy/a udostępnienia formularza komisji i innym inkubatorom",
  equality_and_dnsh: "Będę stosować zasady równościowe i DNSH",
  rodo_info_received: "Potwierdzam wypełnienie wobec mnie obowiązku informacyjnego RODO",
  rodo_duties_fulfilled: "Wypełniłem/am obowiązki informacyjne RODO wobec osób, których dane pozyskałem/am",
};

export const ORG_DECL: Record<string, string> = {
  entity_seat_in_poland: "Podmiot posiada siedzibę (lub oddział) na terenie Polski",
  management_no_conviction: "Członkowie organów / wspólnicy nie byli skazani prawomocnym wyrokiem",
  entity_not_excluded_public_funds: "Podmiot nie jest wykluczony z środków europejskich (art. 207 u.f.p.)",
  entity_not_under_sanctions: "Podmiot nie podlega wykluczeniu z powodu sankcji",
  entity_no_tax_arrears: "Podmiot nie zalega z podatkami, opłatami ani składkami",
  partners_not_employed_rops: "Wspólnicy / członkowie organów nie są zatrudnieni w ROPS ani INNOAGH",
  no_conflict_of_interest: "Brak konfliktu interesów z personelem / władzami ROPS lub INNOAGH",
  not_malopolska_unit: "Podmiot nie jest jednostką / osobą prawną Województwa Małopolskiego",
  not_agh_capital_linked: "Podmiot nie jest powiązany kapitałowo z AGH",
  voluntary_participation: "Dobrowolnie deklaruję uczestnictwo podmiotu w projekcie",
  accepts_procedures: "Zapoznałem/am się z Procedurami i akceptuję warunki",
  data_truthful: "Dane w formularzu są zgodne z prawdą",
  no_parallel_application: "Podmiot nie aplikuje równolegle o wsparcie na ten sam pomysł",
  not_duplicating_existing: "Innowacja nie powiela już wdrożonych / inkubowanych rozwiązań",
  no_fees_from_testers: "Podmiot nie będzie pobierał opłat od osób testujących",
  max_two_applications: "W ramach naboru podmiot składa nie więcej niż 2 aplikacje",
  not_implementation_character: "Innowacja nie ma charakteru wdrożeniowego",
  aware_form_shared: "Jestem świadomy/a udostępnienia formularza komisji i innym inkubatorom",
  equality_and_dnsh: "Będę stosować zasady równościowe i DNSH",
  rodo_info_received: "Potwierdzam wypełnienie wobec mnie obowiązku informacyjnego RODO",
  rodo_duties_fulfilled: "Wypełniłem/am obowiązki informacyjne RODO wobec osób, których dane pozyskałem/am",
};

export const PERSON_FIELDS = [
  ["first_name", "Imię"],
  ["last_name", "Nazwisko"],
  ["address", "Adres korespondencyjny"],
  ["postal_code", "Kod pocztowy"],
  ["city", "Miejscowość"],
  ["phone", "Telefon"],
  ["email", "E-mail"],
] as const;

export const ORG_FIELDS = [
  ["name", "Nazwa podmiotu"],
  ["krs", "KRS"],
  ["regon", "REGON"],
  ["nip", "NIP"],
  ["address", "Adres siedziby"],
  ["postal_code", "Kod pocztowy"],
  ["city", "Miejscowość"],
  ["phone", "Telefon"],
  ["email", "E-mail"],
] as const;

export const CONTACT_FIELDS = [
  ["role", "Funkcja"],
  ["full_name", "Imię i nazwisko"],
  ["phone", "Telefon"],
  ["email", "E-mail"],
] as const;

export const INFORMAL_FIELDS = [
  ["representative_full_name", "Reprezentant — imię i nazwisko"],
  ["representative_phone", "Telefon"],
  ["representative_email", "E-mail"],
] as const;

export const NARRATIVE_SECTIONS = [
  ["description", "3. Opis innowacji"],
  ["innovativeness", "4. Innowacyjność rozwiązania"],
  ["problem_diagnosis", "5. Diagnoza problemu"],
  ["beneficiaries", "6. Opis odbiorców innowacji"],
  ["expected_change", "7. Zmiana jaką wprowadza innowacja"],
  ["future_vision", "8. Wizja przyszłości innowacji"],
] as const;
