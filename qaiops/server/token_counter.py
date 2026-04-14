"""Token counting using tiktoken."""

import logging

import tiktoken

logger = logging.getLogger(__name__)

# 기본 인코딩 (OpenAI 모델 기준, 다른 모델에도 근사값으로 사용)
_DEFAULT_ENCODING = "cl100k_base"


def count_tokens(text: str, model_name: str | None = None) -> int:
    """Count tokens in text using tiktoken.

    Uses the model-specific encoding when available,
    falls back to cl100k_base for unknown models.
    """
    if not text:
        return 0

    try:
        if model_name:
            enc = tiktoken.encoding_for_model(model_name)
        else:
            enc = tiktoken.get_encoding(_DEFAULT_ENCODING)
    except KeyError:
        enc = tiktoken.get_encoding(_DEFAULT_ENCODING)

    return len(enc.encode(text))
