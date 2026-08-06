

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.risk import RISK_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(RISK_DICTIONARY)

RISK_ENTITY_DEFINITION = EntityDefinition(
    RISK_DICTIONARY
)


RISK_LIST_DEFINITION = ListDefinition(
    entity=RISK_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "project"
            ),
            label="Projet",
            width="md",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "reference"
            ),
            label="Référence",
            width="sm",
            truncate=True,
            order=20,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "risk_type"
            ),
            label="Type",
            width="sm",
            order=30,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "title"
            ),
            label="Titre",
            width="lg",
            truncate=True,
            order=40,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "owner"
            ),
            label="Pilote",
            width="md",
            truncate=True,
            order=50,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "criticality"
            ),
            label="Criticité",
            width="sm",
            order=60,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "probability"
            ),
            label="Probabilité",
            width="sm",
            order=70,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "status"
            ),
            label="État",
            width="sm",
            order=80,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "last_review_date"
            ),
            label="Dernière revue",
            width="sm",
            order=90,
        ),
        ColumnDefinition(
            field=RISK_ENTITY_DEFINITION.get_field(
                "is_active"
            ),
            label="Actif",
            width="xs",
            align="center",
            order=100,
        ),
    ),
    default_sort="project",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    RISK_LIST_DEFINITION
)