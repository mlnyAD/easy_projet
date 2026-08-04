

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.work_package import (
    WORK_PACKAGE_DICTIONARY,
)

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
    WORK_PACKAGE_DICTIONARY
)

WORK_PACKAGE_ENTITY_DEFINITION = EntityDefinition(
    WORK_PACKAGE_DICTIONARY
)


WORK_PACKAGE_LIST_DEFINITION = ListDefinition(
    entity=WORK_PACKAGE_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "project"
            ),
            width="lg",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "code"
            ),
            width="sm",
            truncate=True,
            order=20,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "name"
            ),
            width="lg",
            truncate=True,
            order=30,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "manager"
            ),
            label="Responsable",
            width="md",
            truncate=True,
            order=40,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "status"
            ),
            width="sm",
            order=50,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "start_date"
            ),
            label="Début",
            width="sm",
            order=60,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "end_date"
            ),
            label="Fin",
            width="sm",
            order=70,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "planned_workload_hours"
            ),
            label="Charge (h)",
            width="sm",
            align="right",
            order=80,
        ),
        ColumnDefinition(
            field=WORK_PACKAGE_ENTITY_DEFINITION.get_field(
                "is_active"
            ),
            label="Actif",
            width="xs",
            align="center",
            order=90,
        ),
    ),
    default_sort="project",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    WORK_PACKAGE_LIST_DEFINITION
)