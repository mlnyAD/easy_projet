

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.meeting import MEETING_DICTIONARY

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
    MEETING_DICTIONARY
)

MEETING_ENTITY_DEFINITION = EntityDefinition(
    MEETING_DICTIONARY
)


MEETING_LIST_DEFINITION = ListDefinition(
    entity=MEETING_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "project"
            ),
            label="Projet",
            width="md",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "reference"
            ),
            label="Référence",
            width="sm",
            truncate=True,
            order=20,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "subject"
            ),
            label="Objet",
            width="lg",
            truncate=True,
            order=30,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "scheduled_at"
            ),
            label="Date et heure",
            width="md",
            order=40,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "organizer"
            ),
            label="Organisateur",
            width="md",
            truncate=True,
            order=50,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "status"
            ),
            label="État",
            width="sm",
            order=60,
        ),
        ColumnDefinition(
            field=MEETING_ENTITY_DEFINITION.get_field(
                "is_active"
            ),
            label="Active",
            width="xs",
            align="center",
            order=70,
        ),
    ),
    default_sort="scheduled_at",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    MEETING_LIST_DEFINITION
)