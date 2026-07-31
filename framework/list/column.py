

from __future__ import annotations

from dataclasses import dataclass

from framework.dictionary.field import FieldDefinition
from framework.defaults.column import (
    DEFAULT_COLUMN_ALIGN,
    DEFAULT_COLUMN_ORDER,
    DEFAULT_COLUMN_SORTABLE,
    DEFAULT_COLUMN_TRUNCATE,
    DEFAULT_COLUMN_VISIBLE,
    DEFAULT_COLUMN_WIDTH,
)

COLUMN_WIDTHS = frozenset(
    {
        "xs",
        "sm",
        "md",
        "lg",
        "xl",
        "auto",
    }
)
COLUMN_ALIGNMENTS = frozenset(
    {
        "left",
        "center",
        "right",
    }
)


@dataclass(frozen=True, slots=True)
class ColumnDefinition:
    """
    Décrit une colonne d'une liste du Framework Easy Projet.

    La colonne référence directement un FieldDefinition. Elle ne contient
    aucune dépendance à Django, au HTML ou à une technologie de rendu.
    """

    field: FieldDefinition
    identifier: str | None = None
    label: str | None = None
   
    visible: bool = DEFAULT_COLUMN_VISIBLE
    sortable: bool = DEFAULT_COLUMN_SORTABLE
    width: str = DEFAULT_COLUMN_WIDTH
    truncate: bool = DEFAULT_COLUMN_TRUNCATE
    order: int = DEFAULT_COLUMN_ORDER
    align: str = DEFAULT_COLUMN_ALIGN

    def __post_init__(self) -> None:
        self._validate_field()
        self._validate_identifier()
        self._validate_label()
        self._validate_boolean_properties()
        self._validate_width()
        self._validate_order()

        if self.identifier is None:
            object.__setattr__(self, "identifier", self.field.name)

        if self.label is None:
            object.__setattr__(self, "label", self.field.label)

        if not isinstance(self.align, str):
            raise TypeError(
                "La propriété 'align' doit être une chaîne de caractères."
            )

        if self.align not in COLUMN_ALIGNMENTS:
            raise ValueError(
                "La propriété 'align' est invalide."
            )

    @property
    def title(self) -> str:
        """Retourne le libellé effectif de la colonne."""
        return self.label

    def _validate_field(self) -> None:
        if not isinstance(self.field, FieldDefinition):
            raise TypeError(
                "La propriété 'field' doit être une instance de FieldDefinition."
            )

    def _validate_identifier(self) -> None:
        if self.identifier is None:
            return

        if not isinstance(self.identifier, str):
            raise TypeError(
                "La propriété 'identifier' doit être une chaîne de caractères."
            )

        if not self.identifier.strip():
            raise ValueError(
                "La propriété 'identifier' ne peut pas être vide."
            )

    def _validate_label(self) -> None:
        if self.label is None:
            return

        if not isinstance(self.label, str):
            raise TypeError(
                "La propriété 'label' doit être une chaîne de caractères."
            )

        if not self.label.strip():
            raise ValueError(
                "La propriété 'label' ne peut pas être vide."
            )

    def _validate_boolean_properties(self) -> None:
        if not isinstance(self.visible, bool):
            raise TypeError(
                "La propriété 'visible' doit être un booléen."
            )

        if not isinstance(self.sortable, bool):
            raise TypeError(
                "La propriété 'sortable' doit être un booléen."
            )

        if not isinstance(self.truncate, bool):
            raise TypeError(
                "La propriété 'truncate' doit être un booléen."
            )

    def _validate_width(self) -> None:
        if not isinstance(self.width, str):
            raise TypeError(
                "La propriété 'width' doit être une chaîne de caractères."
            )

        if self.width not in COLUMN_WIDTHS:
            raise ValueError(
                "La propriété 'width' doit être l'une des valeurs "
                f"{sorted(COLUMN_WIDTHS)}."
            )

    def _validate_order(self) -> None:
        if isinstance(self.order, bool) or not isinstance(self.order, int):
            raise TypeError(
                "La propriété 'order' doit être un entier."
            )

        if self.order < 0:
            raise ValueError(
                "La propriété 'order' doit être positive ou nulle."
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"field={self.field.name!r}, "
            f"label={self.label!r}, "
            f"width={self.width!r}, "
            f"truncate={self.truncate!r}"
            f")"
        )