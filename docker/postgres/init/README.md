# Postgres init scripts (run once on empty volume)

Mount only this directory into `/docker-entrypoint-initdb.d`.
Do **not** add extra file mounts into that path — Docker Desktop then fails with
`read-only file system` when creating the container.

| File | Source |
|---|---|
| `01-pgvector.sql` | local |
| `02-rag_chunks.sql` … `07-innovations.sql` | copies of `rag/sql/001`…`006` |

After editing `rag/sql/*.sql`, re-copy into this folder (or wipe the volume and recreate).
