

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.license import (
    LICENSE_DICTIONARY,
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
    LICENSE_DICTIONARY,
)

LICENSE_ENTITY_DEFINITION = EntityDefinition(
    LICENSE_DICTIONARY,
)


LICENSE_LIST_DEFINITION = ListDefinition(
    entity=LICENSE_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "reference"
            ),
            order=10,
        ),
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "company_name"
            ),
            order=20,
        ),
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "status_label"
            ),
            order=30,
        ),
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "project_capacity"
            ),
            order=40,
        ),
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "granted_at"
            ),
            order=50,
        ),
        ColumnDefinition(
            field=LICENSE_ENTITY_DEFINITION.get_field(
                "expiration_date"
            ),
            order=60,
        ),
    ),
    default_sort="reference",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(
    LICENSE_LIST_DEFINITION,
)