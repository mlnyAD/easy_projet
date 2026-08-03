

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.user import USER_DICTIONARY

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


DictionaryValidator().validate(USER_DICTIONARY)

USER_ENTITY_DEFINITION = EntityDefinition(USER_DICTIONARY)


USER_LIST_DEFINITION = ListDefinition(
    entity=USER_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("last_name"),
            order=10,
        ),
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("first_name"),
            order=20,
        ),
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("email"),
            order=30,
        ),
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("company"),
            order=40,
        ),
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("global_role"),
            order=50,
        ),
        ColumnDefinition(
            field=USER_ENTITY_DEFINITION.get_field("is_active"),
            order=60,
        ),
    ),
    default_sort="last_name",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(USER_LIST_DEFINITION)