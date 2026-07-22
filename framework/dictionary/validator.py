

from collections.abc import Mapping
from typing import Any


SUPPORTED_DATA_TYPES = {
    "uuid",
    "string",
    "text",
    "boolean",
    "integer",
    "decimal",
    "date",
    "time",
    "datetime",
    "email",
    "phone",
    "postal_code",
    "url",
    "country",
    "currency",
    "percentage",
}

BOOLEAN_FIELD_PROPERTIES = {
    "identifier",
    "required",
    "unique",
}


class DictionaryValidationError(ValueError):
    """Erreur de validation d'un dictionnaire métier."""


class DictionaryValidator:
    """Valide la structure d'un dictionnaire métier Easy Projet."""

    def validate(self, definition: Mapping[str, Any]) -> None:
        self._validate_root(definition)
        self._validate_entity(definition["entity"])
        self._validate_fields(definition["fields"])

    def _validate_root(self, definition: Mapping[str, Any]) -> None:
        if not isinstance(definition, Mapping):
            raise DictionaryValidationError(
                "Le dictionnaire métier doit être une structure de type Mapping."
            )

        for section_name in ("entity", "fields"):
            if section_name not in definition:
                raise DictionaryValidationError(
                    f"La section '{section_name}' est obligatoire."
                )

    def _validate_entity(self, entity: Mapping[str, Any]) -> None:
        if not isinstance(entity, Mapping):
            raise DictionaryValidationError(
                "La section 'entity' doit être de type Mapping."
            )

        for property_name in ("name", "label", "label_plural"):
            self._validate_non_empty_string(
                value=entity.get(property_name),
                error_message=(
                    f"La propriété entity.{property_name} "
                    "doit être une chaîne non vide."
                ),
            )

        description = entity.get("description")

        if description is not None and not isinstance(description, str):
            raise DictionaryValidationError(
                "La propriété entity.description doit être une chaîne."
            )

    def _validate_fields(self, fields: Mapping[str, Any]) -> None:
        if not isinstance(fields, Mapping):
            raise DictionaryValidationError(
                "La section 'fields' doit être de type Mapping."
            )

        if not fields:
            raise DictionaryValidationError(
                "La section 'fields' doit contenir au moins un champ."
            )

        identifier_count = 0

        for field_name, field_definition in fields.items():
            self._validate_field_name(field_name)
            self._validate_field(field_name, field_definition)

            if field_definition.get("identifier", False):
                identifier_count += 1

        if identifier_count != 1:
            raise DictionaryValidationError(
                "Le dictionnaire doit contenir exactement un champ identifiant."
            )

    def _validate_field_name(self, field_name: Any) -> None:
        self._validate_non_empty_string(
            value=field_name,
            error_message=(
                "Chaque nom de champ doit être une chaîne non vide."
            ),
        )

    def _validate_field(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        if not isinstance(field_definition, Mapping):
            raise DictionaryValidationError(
                f"Le champ '{field_name}' doit être défini par un Mapping."
            )

        self._validate_field_label(field_name, field_definition)
        self._validate_field_data_type(field_name, field_definition)
        self._validate_field_description(field_name, field_definition)
        self._validate_field_max_length(field_name, field_definition)
        self._validate_field_boolean_properties(
            field_name,
            field_definition,
        )

    def _validate_field_label(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        self._validate_non_empty_string(
            value=field_definition.get("label"),
            error_message=(
                f"Le champ '{field_name}' doit posséder un label non vide."
            ),
        )

    def _validate_field_data_type(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        data_type = field_definition.get("data_type")

        if data_type not in SUPPORTED_DATA_TYPES:
            raise DictionaryValidationError(
                f"Le champ '{field_name}' utilise un type inconnu : "
                f"{data_type!r}."
            )

    def _validate_field_description(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        description = field_definition.get("description")

        if description is not None and not isinstance(description, str):
            raise DictionaryValidationError(
                f"La description du champ '{field_name}' "
                "doit être une chaîne."
            )

    def _validate_field_max_length(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        max_length = field_definition.get("max_length")

        if max_length is None:
            return

        if isinstance(max_length, bool):
            raise DictionaryValidationError(
                f"Le champ '{field_name}' possède un max_length invalide."
            )

        if not isinstance(max_length, int) or max_length <= 0:
            raise DictionaryValidationError(
                f"Le champ '{field_name}' possède un max_length invalide."
            )

    def _validate_field_boolean_properties(
        self,
        field_name: str,
        field_definition: Mapping[str, Any],
    ) -> None:
        for property_name in BOOLEAN_FIELD_PROPERTIES:
            if property_name not in field_definition:
                continue

            value = field_definition[property_name]

            if not isinstance(value, bool):
                raise DictionaryValidationError(
                    f"La propriété '{property_name}' du champ "
                    f"'{field_name}' doit être un booléen."
                )

    def _validate_non_empty_string(
        self,
        value: Any,
        error_message: str,
    ) -> None:
        if not isinstance(value, str) or not value.strip():
            raise DictionaryValidationError(error_message)