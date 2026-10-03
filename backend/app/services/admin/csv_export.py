import csv
import io
from collections.abc import Iterator

from pydantic import BaseModel


def rows_to_csv(rows: list[BaseModel], fields: list[str]) -> Iterator[str]:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    yield _drain(buf)
    for row in rows:
        data = row.model_dump(mode="json")
        writer.writerow(["" if data[f] is None else data[f] for f in fields])
        yield _drain(buf)


def _drain(buf: io.StringIO) -> str:
    out = buf.getvalue()
    buf.seek(0)
    buf.truncate()
    return out
