

from __future__ import annotations

import os


class IntegrationCredentialResolver:
    """
    Résout une référence de credential depuis l'environnement système.

    La base conserve uniquement une référence, par exemple
    ``DOCUMENSO_API_TOKEN``. La valeur réelle reste dans .env.local,
    un coffre de secrets ou une variable d'environnement de production.
    """

    @staticmethod
    def resolve(
        credential_reference: str,
    ) -> str:
        reference = credential_reference.strip()

        if not reference:
            raise ValueError(
                "La référence de credential est obligatoire."
            )

        value = os.environ.get(reference, "").strip()

        if not value:
            raise ValueError(
                "Aucun credential n'est défini pour la référence "
                f"{reference!r}."
            )

        return value