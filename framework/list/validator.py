

from __future__ import annotations

from framework.list.definition import ListDefinition


class ListValidationError(ValueError):
    """Erreur de validation d'une définition de liste."""


class ListValidator:
    """Valide les règles transversales d'une ListDefinition."""

    def validate(self, definition: ListDefinition) -> None:
        """
        Valide une définition de liste.

        Lève :
            TypeError:
                Si l'objet fourni n'est pas une ListDefinition.

            ListValidationError:
                Si une règle de cohérence transversale n'est pas respectée.
        """
        self._validate_definition_type(definition)
        self._validate_unique_column_identifiers(definition)
        self._validate_column_fields(definition)
        self._validate_default_sort(definition)

    def _validate_definition_type(self, definition: object) -> None:
        if not isinstance(definition, ListDefinition):
            raise TypeError(
                "La définition doit être une instance de ListDefinition."
            )

    def _validate_unique_column_identifiers(
        self,
        definition: ListDefinition,
    ) -> None:
        seen_identifiers: set[str] = set()

        for column in definition.columns:
            identifier = column.identifier

            if identifier in seen_identifiers:
                raise ListValidationError(
                    "L'identifiant de colonne "
                    f"{identifier!r} est déclaré plusieurs fois."
                )

            seen_identifiers.add(identifier)

    def _validate_column_fields(
        self,
        definition: ListDefinition,
    ) -> None:
        entity = definition.entity

        for column in definition.columns:
            field_name = column.field.name

            if not entity.has_field(field_name):
                raise ListValidationError(
                    f"La colonne {column.identifier!r} référence "
                    f"le champ inconnu {field_name!r} pour l'entité "
                    f"{entity.name!r}."
                )

            entity_field = entity.get_field(field_name)

            if column.field is not entity_field:
                raise ListValidationError(
                    f"La colonne {column.identifier!r} ne référence pas "
                    f"le FieldDefinition appartenant à l'entité "
                    f"{entity.name!r}."
                )

    def _validate_default_sort(
        self,
        definition: ListDefinition,
    ) -> None:
        default_sort = definition.default_sort

        if default_sort is None:
            return

        if not definition.has_column(default_sort):
            raise ListValidationError(
                "La colonne de tri par défaut "
                f"{default_sort!r} n'existe pas dans la liste."
            )

        sort_column = definition.get_column(default_sort)

        if not sort_column.sortable:
            raise ListValidationError(
                "La colonne de tri par défaut "
                f"{default_sort!r} n'est pas triable."
            )