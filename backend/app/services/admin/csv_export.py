import csv
import io
from collections.abc import Iterator

from pydantic import BaseModel

# a cell starting with one of these runs as a formula in excel / sheets
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def rows_to_csv(rows: list[BaseModel], fields: list[str]) -> Iterator[str]:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    yield _drain(buf)
    for row in rows:
        data = row.model_dump(mode="json")
        writer.writerow([_cell(data[f]) for f in fields])
        yield _drain(buf)


def _cell(value: object) -> object:
    if value is None:
        return ""
    # citizen text lands in these exports; a leading quote makes it plain text
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def _drain(buf: io.StringIO) -> str:
    out = buf.getvalue()
    buf.seek(0)
    buf.truncate()
    return out
