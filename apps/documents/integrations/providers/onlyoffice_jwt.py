

from __future__ import annotations

from typing import Any

import jwt
from django.conf import settings


class OnlyOfficeJwtService:
    """
    Génération et validation des JWT ONLYOFFICE.

    Le secret partagé est lu depuis la configuration Django.
    """

    ALGORITHM = "HS256"

    @classmethod
    def get_secret(cls) -> str:
        secret = (
            settings.ONLYOFFICE_JWT_SECRET
            .strip()
        )

        if not secret:
            raise RuntimeError(
                "ONLYOFFICE_JWT_SECRET n'est pas configuré."
            )

        return secret

    @classmethod
    def encode(
        cls,
        payload: dict[str, Any],
    ) -> str:
        """
        Signe un payload destiné à ONLYOFFICE.
        """

        if not isinstance(payload, dict):
            raise TypeError(
                "Le payload JWT doit être un dictionnaire."
            )

        return jwt.encode(
            payload,
            cls.get_secret(),
            algorithm=cls.ALGORITHM,
        )

    @classmethod
    def decode(
        cls,
        token: str,
    ) -> dict[str, Any]:
        """
        Vérifie et décode un JWT reçu d'ONLYOFFICE.
        """

        normalized_token = token.strip()

        if not normalized_token:
            raise ValueError(
                "Le token JWT ne peut pas être vide."
            )

        payload = jwt.decode(
            normalized_token,
            cls.get_secret(),
            algorithms=[
                cls.ALGORITHM,
            ],
        )

        if not isinstance(payload, dict):
            raise ValueError(
                "Payload JWT ONLYOFFICE invalide."
            )

        return payload

    @classmethod
    def try_decode(
        cls,
        token: str,
    ) -> dict[str, Any] | None:
        """
        Variante sans exception destinée notamment
        aux vues HTTP.

        Retourne None si le JWT est invalide.
        """

        try:
            return cls.decode(token)
        except (
            ValueError,
            RuntimeError,
            jwt.PyJWTError,
        ):
            return None