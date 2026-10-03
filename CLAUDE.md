# HackYeah 2026 (ROPS social innovation)

Services: `backend/` (match-api: public API + `/admin`), `rag/` (rag service: indexing + retrieval), `frontend/` (Next.js). Each has its own CLAUDE.md.

## Docs stay in sync with decisions

Whenever a change makes a decision or touches architecture, update the docs **in the same change (same PR)**. Examples: a new or renamed service, endpoint, table, field or enum; a change to auth, data flow or delivery semantics; a dropped or deferred feature.

| What changed | Update |
|---|---|
| backend/rag services, endpoints, data model, failure modes | `documentation/backend/architecture.md` (and its Changes list) |
| which requirement a feature covers, or its depth | `documentation/backend/requirements-traceability.md` |
| frontend structure or API usage | `documentation/frontend/architecture.md` |
| a design that was decided or revised | the matching `.claude/designs/<topic>.md`; new design → new file there |

- Names in docs must match the code: same endpoint paths, table and field names.
- Remove superseded content instead of leaving "was X" notes. Git history keeps the old version.
- If the docs and the code disagree, say so in the PR. Don't silently pick one.
