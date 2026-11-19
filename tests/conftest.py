"""Keep service tests independent of live databases and model credentials."""

import os
from contextlib import ExitStack
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


_external_services = ExitStack()
_external_services.enter_context(
    patch.dict(
        os.environ,
        {
            "WEAVIATE_URL": "https://test.invalid",
            "WEAVIATE_API_KEY": "test-key",
            "GEMINI_API_KEY": "test-key",
            "GROQ_API_KEY": "test-key",
            "GROQ_API_KEY_B": "test-key",
            "GRADIO_ANALYTICS_ENABLED": "False",
            "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        },
    )
)
_external_services.enter_context(
    patch("weaviate.connect_to_weaviate_cloud", return_value=MagicMock())
)
# Elysia imports/downloads a spaCy model at import time. Replace that external
# runtime at the module boundary so CI never downloads a model or needs a key.
_elysia = ModuleType("elysia")
_elysia.configure = MagicMock()
_elysia.tool = lambda function: function
_elysia.Tree = MagicMock()
_external_services.enter_context(patch.dict("sys.modules", {"elysia": _elysia}))


@pytest.fixture(autouse=True)
def block_live_connections(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("Tests must mock external services instead of connecting")

    monkeypatch.setattr("socket.socket.connect", fail)


def pytest_unconfigure(config):
    _external_services.close()
