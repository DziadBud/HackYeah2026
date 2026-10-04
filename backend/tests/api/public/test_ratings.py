import pytest


@pytest.mark.parametrize(
    ("rating", "checked"),
    [("4", 'value="4" required checked'), ("9", None), (None, None)],
    ids=["#1 - OK - prefilled", "#2 - OK - out of range ignored", "#3 - OK - no rating"],
)
def test_rating_form(client, rating, checked) -> None:
    params = {"rating": rating} if rating else {}
    res = client.get("/ratings/signup-accepted", params=params)
    assert res.status_code == 200
    assert "Jak sprawdził się „Wibraap”?" in res.text
    if checked:
        assert checked in res.text
    else:
        assert " checked" not in res.text


def test_rating_link_alone_stores_nothing(client, fresh_services) -> None:
    # link scanners open every url in a mail; only the button saves
    client.get("/ratings/signup-accepted", params={"rating": "5"})
    assert fresh_services.feedback == []


def test_submit_rating(client, fresh_services) -> None:
    res = client.post("/ratings/signup-accepted", data={"stars": "4", "comment": "Działa, ale instrukcja za długa"})
    assert res.status_code == 200
    assert "Dziękujemy za ocenę!" in res.text
    assert fresh_services.feedback == [("signup-accepted", 4, "Działa, ale instrukcja za długa")]


def test_second_rating_not_stored(client, fresh_services) -> None:
    client.post("/ratings/signup-accepted", data={"stars": "4"})
    res = client.post("/ratings/signup-accepted", data={"stars": "1"})
    assert "Ta ocena jest już zapisana" in res.text
    assert len(fresh_services.feedback) == 1
    assert "Ta ocena jest już zapisana" in client.get("/ratings/signup-accepted").text


@pytest.mark.parametrize(
    "signup_id",
    ["signup-applied", "missing"],
    ids=["#1 - FAIL - not accepted yet", "#2 - FAIL - unknown link"],
)
def test_rating_unavailable(client, fresh_services, signup_id) -> None:
    assert client.get(f"/ratings/{signup_id}").status_code == 404
    res = client.post(f"/ratings/{signup_id}", data={"stars": "5"})
    assert res.status_code == 404 and "Ten link nie działa" in res.text
    assert fresh_services.feedback == []


@pytest.mark.parametrize(
    "data",
    [{"stars": "0"}, {"stars": "6"}, {}, {"stars": "3", "comment": "x" * 2001}],
    ids=["#1 - FAIL - zero", "#2 - FAIL - six", "#3 - FAIL - missing", "#4 - FAIL - comment too long"],
)
def test_submit_rating_invalid(client, fresh_services, data) -> None:
    assert client.post("/ratings/signup-accepted", data=data).status_code == 422
    assert fresh_services.feedback == []

