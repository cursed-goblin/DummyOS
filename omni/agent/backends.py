"""Pluggable model backends.

The agent can adapt to any local Hugging Face model by swapping the backend.
The ``echo`` backend has zero dependencies and is used for tests / demos.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ModelBackend:
    """Common interface every backend implements."""

    def load_model(self, model_path: str, context_length: int = 4096) -> None:
        raise NotImplementedError

    def generate(self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError

    def supports_tools(self) -> bool:
        return False

    def max_context_length(self) -> int:
        return 4096


class EchoBackend(ModelBackend):
    """Dependency-free backend that echoes the prompt. Useful for tests."""

    def load_model(self, model_path: str = "", context_length: int = 4096) -> None:
        self._ctx = context_length

    def generate(self, prompt: str, tools=None, context=None) -> str:
        return f"echo: {prompt}"

    def supports_tools(self) -> bool:
        return True

    def max_context_length(self) -> int:
        return getattr(self, "_ctx", 4096)


class LlamaCppBackend(ModelBackend):
    """llama.cpp / GGUF backend. Requires `pip install llama-cpp-python`."""

    def __init__(self) -> None:
        self.model = None
        self._ctx = 4096

    def load_model(self, model_path: str, context_length: int = 4096) -> None:
        from llama_cpp import Llama  # imported lazily

        self._ctx = context_length
        self.model = Llama(
            model_path=model_path,
            n_ctx=context_length,
            n_gpu_layers=-1,
        )

    def generate(self, prompt: str, tools=None, context=None, max_tokens: int = 512) -> str:
        if self.model is None:
            raise RuntimeError("No model loaded")
        out = self.model(prompt, max_tokens=max_tokens, stop=["</tool_call>", "</s>"])
        return out["choices"][0]["text"]

    def supports_tools(self) -> bool:
        return True

    def max_context_length(self) -> int:
        return self._ctx


class TransformersBackend(ModelBackend):
    """Hugging Face Transformers backend. Requires `pip install transformers torch`."""

    def __init__(self) -> None:
        self.pipe = None
        self._ctx = 4096

    def load_model(self, model_path: str, context_length: int = 4096) -> None:
        from transformers import pipeline  # imported lazily

        self._ctx = context_length
        self.pipe = pipeline("text-generation", model=model_path)

    def generate(self, prompt: str, tools=None, context=None, max_new_tokens: int = 512) -> str:
        if self.pipe is None:
            raise RuntimeError("No model loaded")
        out = self.pipe(prompt, max_new_tokens=max_new_tokens)
        return out[0]["generated_text"]

    def max_context_length(self) -> int:
        return self._ctx


_BACKENDS = {
    "echo": EchoBackend,
    "llama.cpp": LlamaCppBackend,
    "transformers": TransformersBackend,
}


def get_backend(name: str) -> ModelBackend:
    try:
        return _BACKENDS[name]()
    except KeyError as exc:
        raise ValueError(
            f"Unknown backend {name!r}; available: {sorted(_BACKENDS)}"
        ) from exc
