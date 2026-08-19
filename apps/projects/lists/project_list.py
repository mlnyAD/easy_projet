

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.project import PROJECT_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(PROJECT_DICTIONARY)

PROJECT_ENTITY_DEFINITION = EntityDefinition(
    PROJECT_DICTIONARY
)


PROJECT_LIST_DEFINITION = ListDefinition(
    entity=PROJECT_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "reference"
            ),
            width="sm",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "name"
            ),
            width="lg",
            truncate=True,
            order=20,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "owner_company"
            ),
            label="Maître d’ouvrage",
            width="lg",
            truncate=True,
            order=30,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "project_manager"
            ),
            label="Chef de projet",
            width="md",
            truncate=True,
            order=40,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "status"
            ),
            width="sm",
            order=50,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "start_date"
            ),
            label="Début",
            width="sm",
            order=60,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "end_date"
            ),
            label="Fin",
            width="sm",
            order=70,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "receipt_date"
            ),
            label="Réception",
            width="sm",
            order=80,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "delivery_date"
            ),
            label="Livraison",
            width="sm",
            order=90,
        ),
        ColumnDefinition(
            field=PROJECT_ENTITY_DEFINITION.get_field(
                "is_active"
            ),
            label="Actif",
            width="xs",
            align="center",
            order=100,
        ),
    ),
    default_sort="reference",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    PROJECT_LIST_DEFINITION
)