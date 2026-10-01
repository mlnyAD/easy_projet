

from __future__ import annotations

from collections.abc import Iterable

from apps.users.models import UserListPreference
from framework.list import ListDefinition


class UserListPreferenceService:
    """
    Gestion des préférences d'affichage des listes par utilisateur.

    Les colonnes sont toujours restituées dans l'ordre déclaré par
    ListDefinition, même si elles ont été reçues dans un autre ordre.
    """

    @classmethod
    def get_visible_column_identifiers(
        cls,
        *,
        user,
        definition: ListDefinition,
    ) -> tuple[str, ...]:
        """
        Retourne les colonnes visibles pour cet utilisateur et cette liste.

        En l'absence de préférence, la visibilité définie par la liste
        est utilisée. Une préférence devenue obsolète est tolérée :
        les identifiants inconnus sont ignorés.
        """

        default_identifiers = cls._get_default_identifiers(
            definition=definition,
        )

        preference = (
            UserListPreference.objects.filter(
                user=user,
                list_identifier=definition.identifier,
            )
            .only("visible_column_identifiers")
            .first()
        )

        if preference is None:
            return default_identifiers

        selected_identifiers = (
            preference.visible_column_identifiers
        )

        if not isinstance(selected_identifiers, list):
            return default_identifiers

        valid_identifiers = {
            identifier
            for identifier in selected_identifiers
            if (
                isinstance(identifier, str)
                and definition.has_column(identifier)
            )
        }

        if not valid_identifiers:
            return default_identifiers

        return tuple(
            column.identifier
            for column in definition.columns
            if column.identifier in valid_identifiers
        )

    @classmethod
    def save_visible_column_identifiers(
        cls,
        *,
        user,
        definition: ListDefinition,
        identifiers: Iterable[str],
    ) -> UserListPreference:
        """
        Enregistre les colonnes visibles choisies par l'utilisateur.

        Au moins une colonne doit rester visible. Les identifiants
        inconnus et les doublons sont refusés.
        """

        normalized_identifiers = cls._normalize_identifiers(
            definition=definition,
            identifiers=identifiers,
        )

        preference, _ = (
            UserListPreference.objects.update_or_create(
                user=user,
                list_identifier=definition.identifier,
                defaults={
                    "visible_column_identifiers": list(
                        normalized_identifiers
                    ),
                },
            )
        )

        return preference

    @staticmethod
    def _get_default_identifiers(
        *,
        definition: ListDefinition,
    ) -> tuple[str, ...]:
        return tuple(
            column.identifier
            for column in definition.visible_columns
        )

    @classmethod
    def _normalize_identifiers(
        cls,
        *,
        definition: ListDefinition,
        identifiers: Iterable[str],
    ) -> tuple[str, ...]:
        if isinstance(identifiers, (str, bytes)):
            raise TypeError(
                "Les identifiants de colonnes doivent être "
                "un itérable de chaînes."
            )

        try:
            received_identifiers = tuple(identifiers)
        except TypeError as error:
            raise TypeError(
                "Les identifiants de colonnes doivent être "
                "un itérable de chaînes."
            ) from error

        if not received_identifiers:
            raise ValueError(
                "Au moins une colonne doit rester visible."
            )

        seen_identifiers = set()

        for identifier in received_identifiers:
            if not isinstance(identifier, str):
                raise TypeError(
                    "Chaque identifiant de colonne doit être "
                    "une chaîne de caractères."
                )

            if not identifier.strip():
                raise ValueError(
                    "Un identifiant de colonne ne peut pas être vide."
                )

            if identifier in seen_identifiers:
                raise ValueError(
                    "Un identifiant de colonne ne peut pas être "
                    "présent plusieurs fois."
                )

            if not definition.has_column(identifier):
                raise ValueError(
                    f"La colonne {identifier!r} n'existe pas "
                    "dans cette liste."
                )

            seen_identifiers.add(identifier)

        return tuple(
            column.identifier
            for column in definition.columns
            if column.identifier in seen_identifiers
        )