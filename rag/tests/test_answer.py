from app.services.answer import AnswerService


class DownOllama:
    def generate(self, prompt: str) -> object:
        raise RuntimeError("Ollama request failed")


def test_answer_is_empty_when_ollama_is_down():
    service = AnswerService(client=DownOllama())

    assert service.generate("seniorzy samotni", [{"innovation_id": "wibraap"}]) == ""
