---
name: hubmi-challenge-criteria
description: Judging criteria and hard requirements of the ROPS Kraków "Małopolski Hub Innowacji Społecznych" HackYeah 2026 challenge. Load before designing, building, cutting or prioritising any feature, before touching UI/accessibility, before writing pitch/demo/deliverable material, and whenever deciding what to build next or whether something is worth the time.
---

# HubMI challenge: what the jury scores and what to watch for

Source: `documentation/knowledge-base/CRITERIA-Wojewodztwo-Malopolskie-HUBMI.md` (full Polish text). Per-requirement implementation map: `documentation/backend/requirements-traceability.md`. Read those when you need detail; this file is the checklist.

## Scoring (100%)

| Criterion | Weight | What it means for us |
|---|---|---|
| Stopień spełnienia wyzwania | 40% | Matchmaking = 10%, **each further module +5%**. Quality of the key elements counts, not just presence. |
| Potencjał wdrożeniowy | 20% | Practical use, scalability, flexibility, cost efficiency, simple maintenance. |
| Dostępność i intuicyjność | 20% | Clear for every age and digital skill level; designed toward **WCAG 2.1 AA**. |
| Atrakcyjność, pomysłowość, jakość UI | 10% | Novel, non-template approach; visual quality of UX/UI mockups. |
| Jakość materiałów i MVP | 10% | How the concept is communicated; quality of submitted materials. |

Implication: a module that works end to end beats two half-finished ones, but each extra *working* module is worth +5%. Never trade away matchmaking quality or accessibility for another module.

## Modules (names may be changed, functionality may not)

1. **Matchmaking społeczny — MANDATORY.** User describes a problem → system finds similar cases/info and proposes ready innovations. Judged on *trafność dopasowania*: does it suggest the right existing innovation from keywords in the need description? Must work in the demo, every time.
2. **Zasobnik wiedzy** — Małopolska challenges (reports, Mapa Wyzwań Społecznych), Biblioteka Innowacji Społecznych (attractive presentation, incl. films), educational materials. Must allow **fast data updates**. Aggregated needs/trends are **admin-only**.
3. **Kreator pomysłów** — idea card ("fiszka": short description, essence, target group, stage) always available; **grant application generator only while a grant call is open**, tailored per call; Canvas Innowacji Społecznych materials; nice-to-have AI assistant (develops the idea, suggests unusual solutions, visualises it).
4. **Tester innowacji** — sign up to test, rate existing solutions, give feedback, propose improvements.
5. **Platforma aktywnej komunikacji** — direct ROPS ↔ user dialogue, quick questions, mentor support, cross-sector partnerships.
6. **Panel administratora** — fast editing, verification and publishing of knowledge.
7. **Middleman innowacji** — AI assistant adapting an innovation into a service for the requesting institution's needs.

## Users — every feature should serve at least one

- **Mieszkańcy / NGOs** — report ideas and problems; need a simple interface, clear process, quick communication.
- **JST (local government)** — diagnose and report local challenges *and* browse a catalogue of ready innovations to implement.
- **ROPS staff** — admins/coordinators; need a clear panel for knowledge, monitoring submissions and dialogue.
- **Eksperci branżowi** — consultants for innovators and JST; need fast feedback and collaboration tools.

## What the jury explicitly tests

- **Intuicyjność:** can a resident of any age, with low digital skills and no preparation, fill in the modules and find information? → plain Polish, few steps, no jargon, obvious next action.
- **Szybkość komunikacji:** *how is the admin notified about a new idea, and what is the reply path back to the author?* Have a concrete, demoable answer (notification → admin inbox → reply → author gets it).
- **Trafność dopasowania:** keyword-based need descriptions must surface the right innovations. Test with `documentation/sample-data/sample-matchmaking-queries.md`.
- **Pomysłowość:** not just re-hosting features of existing portals; show a new quality.
- Also weighed: ease of reporting a problem, quality of communication between users, potential for further development.

## Hard requirements and traps

- **Accessibility (WCAG 2.1 AA)** is 20% on its own and a stated requirement for seniors and people with disabilities: contrast, keyboard navigation, focus visible, form labels, alt text, text-size control, no time limits, readable error messages. Flag any UI change that breaks these.
- **No real personal or sensitive data** from ROPS materials. Seed/demo data must be fictional. Don't paste real names, emails or case details into fixtures, prompts or logs.
- **Data security** must be considered (admin auth, rate limits on LLM endpoints, no secrets in the repo).
- **Scalable and integration-ready**: whole-voivodeship data and many concurrent users; future integration with Hub systems (e.g. grant database); **automated notifications about new ideas and grant-call changes**.
- **AI is expected** — the platform should use AI, and the pitch must show how technology speeds up the Hub's work and the spread of innovations. But AI output must be grounded in our data (no invented innovations or figures).
- **Cost of operation** is a required deliverable and feeds the 20% deployment criterion — keep infra cheap and easy to maintain; avoid adding paid services without a reason.

## Required deliverables (submission)

- Name and description of the solution.
- PDF presentation (**max 10 slides**) or video (**max 3 minutes**).
- Link to a **working demo** and to **UX/UI mockups** (mockups are the minimum visual requirement).
- Expected maintenance/operating cost and the resources needed.

## How to use this when working

- Prioritising work: matchmaking quality → accessibility → finishing extra modules end to end → UI polish → materials.
- Before cutting or deferring a feature, state which module/criterion it costs points in.
- When adding a feature, check it maps to a module above and a user group; update `documentation/backend/requirements-traceability.md` per the root CLAUDE.md.
- When writing pitch or demo material, cover: which modules work, the admin-notification→reply path, a matchmaking example with a correct hit, accessibility measures, and running cost.
