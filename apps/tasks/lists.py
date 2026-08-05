

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.task import TASK_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(TASK_DICTIONARY)

TASK_ENTITY_DEFINITION = EntityDefinition(
    TASK_DICTIONARY
)


TASK_LIST_DEFINITION = ListDefinition(
    entity=TASK_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "work_package"
            ),
            label="Lot",
            width="md",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "status"
            ),
            label="Statut",
            width="sm",
            order=20,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "code"
            ),
            label="Code",
            width="sm",
            truncate=True,
            order=30,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "name"
            ),
            label="Nom",
            width="lg",
            truncate=True,
            order=40,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "effective_start_date"
            ),
            label="Début",
            sortable=False,
            width="sm",
            order=50,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "effective_end_date"
            ),
            label="Fin",
            sortable=False,
            width="sm",
            order=60,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "planned_workload_hours"
            ),
            label="Charge (h)",
            width="sm",
            align="right",
            order=70,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "remaining_workload_hours"
            ),
            label="RAF (h)",
            width="sm",
            align="right",
            order=80,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "progress_percent"
            ),
            label="Avancement",
            width="sm",
            align="right",
            order=90,
        ),
        ColumnDefinition(
            field=TASK_ENTITY_DEFINITION.get_field(
                "is_active"
            ),
            label="Active",
            width="xs",
            align="center",
            order=100,
        ),
    ),
    default_sort="work_package",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    TASK_LIST_DEFINITION
)