import csv
import io

import pytest
from pydantic import BaseModel

from app.services.admin.csv_export import rows_to_csv


class Row(BaseModel):
    text: str | None
    count: int


@pytest.mark.parametrize(
    "text, want",
    [
        pytest.param("brak busa", "brak busa", id="#1 - OK - plain text untouched"),
        pytest.param(None, "", id="#2 - OK - null is empty"),
        pytest.param('=HYPERLINK("http://evil","x")', '\'=HYPERLINK("http://evil","x")', id="#3 - OK - formula escaped"),
        pytest.param("+48 600", "'+48 600", id="#4 - OK - plus escaped"),
        pytest.param("@SUM(A1)", "'@SUM(A1)", id="#5 - OK - at escaped"),
    ],
)
def test_rows_to_csv_escapes_formulas(text, want) -> None:
    out = "".join(rows_to_csv([Row(text=text, count=-3)], ["text", "count"]))
    _, row = csv.reader(io.StringIO(out))
    # numbers are not text, so a negative count stays a number
    assert row == [want, "-3"]
