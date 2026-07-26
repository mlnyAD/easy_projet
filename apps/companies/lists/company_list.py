

from common.constants.common import DEFAULT_PAGE_SIZE
from common.dictionaries.company import COMPANY_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(COMPANY_DICTIONARY)

COMPANY_ENTITY_DEFINITION = EntityDefinition(COMPANY_DICTIONARY)


COMPANY_LIST_DEFINITION = ListDefinition(
    entity=COMPANY_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("name"),
            order=10,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("siret"),
            order=20,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("email"),
            order=30,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("phone"),
            order=40,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("city"),
            order=50,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("is_active"),
            order=60,
        ),
    ),
    default_sort="name",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(COMPANY_LIST_DEFINITION)