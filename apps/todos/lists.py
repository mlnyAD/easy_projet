

from common.constants import DEFAULT_PAGE_SIZE

from common.dictionaries.todo import TODO_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)

from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(
    TODO_DICTIONARY
)

TODO_ENTITY_DEFINITION = EntityDefinition(
    TODO_DICTIONARY
)


TODO_LIST_DEFINITION = ListDefinition(
    entity=TODO_ENTITY_DEFINITION,

    columns=(
        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "status_label"
            ),
            label="État",
            width="sm",
            order=10,
        ),

        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "title"
            ),
            label="Action",
            width="lg",
            truncate=True,
            order=20,
        ),

        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "due_date"
            ),
            label="Échéance",
            width="sm",
            order=30,
        ),

        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "project"
            ),
            label="Projet",
            width="md",
            truncate=True,
            order=40,
        ),

        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "origin_label"
            ),
            label="Origine",
            width="sm",
            order=50,
        ),

        ColumnDefinition(
            field=TODO_ENTITY_DEFINITION.get_field(
                "role_label"
            ),
            label="Rôle",
            width="sm",
            order=60,
        ),
    ),

    default_sort="due_date",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    TODO_LIST_DEFINITION
)