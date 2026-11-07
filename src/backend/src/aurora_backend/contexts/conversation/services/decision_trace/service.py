"""Registra um evento por resposta gerada, só com metadados (plano §5.7, R-07).

Campos fora da lista permitida são descartados: mensagem, resposta e trechos nunca
chegam ao log, mesmo que um chamador os passe por engano.
"""

import json
import logging
import uuid
from typing import Any

logger = logging.getLogger("uvicorn.error.aurora.trace")

ALLOWED_FIELDS = frozenset(
    {
        "outcome",
        "provider",
        "model",
        "kb_version",
        "prompt_version",
        "guardrail_version",
        "guardrail_violations",
        "source_ids",
        "cited_source_ids",
        "segments",
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "duration_ms",
        "error",
    }
)


class DecisionTraceService:
    def record(self, event: str, **fields: Any) -> None:
        payload = {key: value for key, value in fields.items() if key in ALLOWED_FIELDS}
        payload = {"event": event, "trace_id": uuid.uuid4().hex[:12], **payload}
        logger.info(json.dumps(payload, ensure_ascii=False, default=str))
