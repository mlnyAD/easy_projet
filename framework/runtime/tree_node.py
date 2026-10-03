

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from framework.tree import TreeNodeKind


_DATA_ATTRIBUTE_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9-]*$"
)


@dataclass(frozen=True, slots=True)
class TreeNode:
    """
    Nœud exécutable d'une arborescence.

    Les attributs data permettent à une intégration applicative
    d'associer des commandes métier à un nœud sans rendre le
    framework dépendant de cette application.
    """

    identifier: str
    parent_identifier: str | None
    label: str
    kind: TreeNodeKind
    source_object: object
    icon: str | None = None
    url: str | None = None
    is_disabled: bool = False
    data_attributes: Mapping[str, str] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        self._validate_identifier(
            self.identifier,
            "identifier",
        )
        self._validate_parent_identifier(
            self.parent_identifier,
        )
        self._validate_label(self.label)
        self._validate_kind(self.kind)
        self._validate_source_object(
            self.source_object,
        )
        self._validate_optional_string(
            self.icon,
            "icon",
        )
        self._validate_optional_string(
            self.url,
            "url",
        )
        self._validate_is_disabled(
            self.is_disabled,
        )

        normalized_attributes = (
            self._normalize_data_attributes(
                self.data_attributes,
            )
        )

        object.__setattr__(
            self,
            "data_attributes",
            MappingProxyType(
                normalized_attributes,
            ),
        )

    @staticmethod
    def _validate_identifier(
        value: object,
        property_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"La propriété '{property_name}' doit être "
                "une chaîne de caractères."
            )

        if not value.strip():
            raise ValueError(
                f"La propriété '{property_name}' ne peut pas "
                "être vide."
            )

    @classmethod
    def _validate_parent_identifier(
        cls,
        value: object,
    ) -> None:
        if value is None:
            return

        cls._validate_identifier(
            value,
            "parent_identifier",
        )

    @staticmethod
    def _validate_label(value: object) -> None:
        if not isinstance(value, str):
            raise TypeError(
                "La propriété 'label' doit être une chaîne "
                "de caractères."
            )

        if not value.strip():
            raise ValueError(
                "La propriété 'label' ne peut pas être vide."
            )

    @staticmethod
    def _validate_kind(value: object) -> None:
        if not isinstance(value, TreeNodeKind):
            raise TypeError(
                "La propriété 'kind' doit être une instance "
                "de TreeNodeKind."
            )

    @staticmethod
    def _validate_source_object(value: object) -> None:
        if value is None:
            raise ValueError(
                "La propriété 'source_object' ne peut pas "
                "être nulle."
            )

    @staticmethod
    def _validate_optional_string(
        value: object,
        property_name: str,
    ) -> None:
        if value is None:
            return

        if not isinstance(value, str):
            raise TypeError(
                f"La propriété '{property_name}' doit être "
                "une chaîne de caractères ou None."
            )

        if not value.strip():
            raise ValueError(
                f"La propriété '{property_name}' ne peut pas "
                "être vide."
            )

    @staticmethod
    def _validate_is_disabled(value: object) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                "La propriété 'is_disabled' doit être "
                "un booléen."
            )

    @classmethod
    def _normalize_data_attributes(
        cls,
        value: object,
    ) -> dict[str, str]:
        if not isinstance(value, Mapping):
            raise TypeError(
                "La propriété 'data_attributes' doit être "
                "un Mapping."
            )

        normalized_attributes: dict[str, str] = {}

        for name, attribute_value in value.items():
            if not isinstance(name, str):
                raise TypeError(
                    "Chaque nom d'attribut de données doit être "
                    "une chaîne de caractères."
                )

            normalized_name = name.strip()

            if not normalized_name:
                raise ValueError(
                    "Un nom d'attribut de données ne peut pas "
                    "être vide."
                )

            if normalized_name.startswith("data-"):
                raise ValueError(
                    "Le nom d'un attribut de données ne doit pas "
                    "inclure le préfixe 'data-'."
                )

            if not _DATA_ATTRIBUTE_NAME_PATTERN.fullmatch(
                normalized_name
            ):
                raise ValueError(
                    "Le nom d'un attribut de données doit utiliser "
                    "des lettres minuscules, des chiffres ou des "
                    "tirets."
                )

            if not isinstance(attribute_value, str):
                raise TypeError(
                    "La valeur d'un attribut de données doit être "
                    "une chaîne de caractères."
                )

            normalized_attributes[normalized_name] = (
                attribute_value
            )

        return normalized_attributes