import pytest

REQUEST = {"innovation_id": "wibraap", "institution_type": "gmina", "needs": "Szkoła z uczniami niesłyszącymi"}


def test_middleman_stores_document(client) -> None:
    res = client.post("/middleman", json=REQUEST)

    assert res.status_code == 201
    doc = res.json()
    assert doc["kind"] == "middleman"
    assert "Wibraap" in doc["output"]


@pytest.mark.parametrize(
    "override, want",
    [
        pytest.param({"innovation_id": "nope"}, 404, id="#1 - FAIL - unknown innovation"),
        pytest.param({"institution_type": "bank"}, 422, id="#2 - FAIL - unknown institution type"),
    ],
)
def test_middleman_failures(client, override, want) -> None:
    assert client.post("/middleman", json={**REQUEST, **override}).status_code == want

