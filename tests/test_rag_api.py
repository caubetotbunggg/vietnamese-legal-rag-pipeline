import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.models.rag_model import RAGResponse
from app.services import rag_service


client = TestClient(app)


def test_demo_and_openapi_are_mounted():
    assert client.get("/").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/rag", "/retrieve", "/health"} <= paths.keys()


def test_rag_endpoint_returns_answer_and_reasoning(monkeypatch):
    monkeypatch.setattr(
        rag_service.RAGService,
        "rag_pipeline",
        lambda request: RAGResponse(answer=request.user_input, reasoning="source text"),
    )
    response = client.post("/rag", params={"user_input": "Câu hỏi pháp luật"})
    assert response.status_code == 200
    assert response.json() == {
        "answer": "Câu hỏi pháp luật",
        "reasoning": "source text",
    }


def test_rag_endpoint_rejects_blank_question():
    assert client.post("/rag", params={"user_input": "  "}).status_code == 400
    assert client.post("/rag").status_code == 422


def test_answer_generation_retries_empty_choices(monkeypatch):
    call = MagicMock(
        side_effect=[
            SimpleNamespace(choices=[]),
            SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Answer"))]
            ),
        ]
    )
    monkeypatch.setattr(rag_service.GROQ_CLIENT_B.chat.completions, "create", call)
    monkeypatch.setattr(rag_service.asyncio, "sleep", AsyncMock())
    answer = asyncio.run(rag_service._get_llm_response_with_timeout("prompt"))
    assert answer == "Answer"
    assert call.call_count == 2
