

from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.models.base import TimeStampedModel


class UserListPreference(TimeStampedModel):
    """
    Préférences d'affichage d'une liste pour un utilisateur.

    La préférence porte actuellement sur les colonnes visibles.
    Les filtres, le tri et la pagination restent dans l'URL,
    car ils représentent un contexte temporaire de consultation.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="list_preferences",
        verbose_name="Utilisateur",
    )

    list_identifier = models.CharField(
        max_length=100,
        verbose_name="Identifiant de liste",
    )

    visible_column_identifiers = models.JSONField(
        default=list,
        verbose_name="Colonnes visibles",
    )

    class Meta:
        db_table = "user_list_preference"
        ordering = [
            "user",
            "list_identifier",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "list_identifier",
                ],
                name="uq_user_list_pref_user_list",
            ),
        ]
        verbose_name = "Préférence de liste utilisateur"
        verbose_name_plural = (
            "Préférences de listes utilisateur"
        )

    def clean(self) -> None:
        super().clean()

        if not self.list_identifier.strip():
            raise ValidationError(
                {
                    "list_identifier": (
                        "L'identifiant de liste est obligatoire."
                    ),
                }
            )

        column_identifiers = (
            self.visible_column_identifiers
        )

        if not isinstance(
            column_identifiers,
            list,
        ):
            raise ValidationError(
                {
                    "visible_column_identifiers": (
                        "Les colonnes visibles doivent être "
                        "fournies sous forme de liste."
                    ),
                }
            )

        if not all(
            isinstance(identifier, str)
            and identifier.strip()
            for identifier in column_identifiers
        ):
            raise ValidationError(
                {
                    "visible_column_identifiers": (
                        "Chaque identifiant de colonne doit être "
                        "une chaîne non vide."
                    ),
                }
            )

        if len(set(column_identifiers)) != len(
            column_identifiers
        ):
            raise ValidationError(
                {
                    "visible_column_identifiers": (
                        "Une colonne ne peut pas être déclarée "
                        "plusieurs fois."
                    ),
                }
            )

    def __str__(self) -> str:
        return (
            f"{self.user} — "
            f"{self.list_identifier}"
        )