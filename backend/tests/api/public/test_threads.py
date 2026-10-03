THREAD = {"title": "Pytanie", "body": "Jak to wdrożyć w gminie?", "author_label": "Urzędnik, Bochnia"}


def test_published_threads_with_replies(client) -> None:
    threads = client.get("/innovations/wibraap/threads").json()
    assert threads[0]["id"] == "thread-wibraap-1"
    assert len(threads[0]["replies"]) == 1


def test_new_thread_waits_for_moderation(client) -> None:
    res = client.post("/innovations/wibraap/threads", json=THREAD)

    assert res.status_code == 202
    assert res.json()["status"] == "pending"
    assert len(client.get("/innovations/wibraap/threads").json()) == 1


def test_reply_waits_for_moderation(client) -> None:
    res = client.post("/threads/thread-wibraap-1/replies", json={"body": "U nas działa", "author_label": "NGO"})
    assert res.status_code == 202
    assert res.json()["status"] == "pending"


def test_unknown_thread_404(client) -> None:
    assert client.post("/threads/nope/replies", json={"body": "x", "author_label": "y"}).status_code == 404


def test_thread_on_draft_innovation_404(client) -> None:
    assert client.post("/innovations/paszport-choroby-rzadkiej/threads", json=THREAD).status_code == 404
