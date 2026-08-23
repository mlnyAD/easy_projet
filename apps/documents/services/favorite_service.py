

from __future__ import annotations

from django.db import transaction

from apps.documents.models import (
    Document,
    DocumentFavorite,
)
from apps.users.models import User


class DocumentFavoriteService:
    """
    Gestion des favoris documentaires personnels.
    """

    @staticmethod
    @transaction.atomic
    def add_favorite(
        *,
        user: User,
        document: Document,
    ) -> DocumentFavorite:
        """
        Ajoute un document aux favoris de l'utilisateur.

        L'opération est idempotente.
        """

        favorite, _ = (
            DocumentFavorite.objects
            .get_or_create(
                user=user,
                document=document,
            )
        )

        return favorite

    @staticmethod
    @transaction.atomic
    def remove_favorite(
        *,
        user: User,
        document: Document,
    ) -> None:
        """
        Retire un document des favoris de l'utilisateur.

        L'opération est idempotente.
        """

        (
            DocumentFavorite.objects
            .filter(
                user=user,
                document=document,
            )
            .delete()
        )

    @staticmethod
    def is_favorite(
        *,
        user: User,
        document: Document,
    ) -> bool:
        """
        Indique si le document est favori
        pour l'utilisateur.
        """

        return (
            DocumentFavorite.objects
            .filter(
                user=user,
                document=document,
            )
            .exists()
        )