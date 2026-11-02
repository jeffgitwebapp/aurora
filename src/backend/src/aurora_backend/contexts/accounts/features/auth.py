"""Leitura do token de sessão compartilhada pelas features de Contas."""

from fastapi import HTTPException, status

_BEARER_PREFIX = "Bearer "


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith(_BEARER_PREFIX):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão encerrada.")
    return authorization.removeprefix(_BEARER_PREFIX)
