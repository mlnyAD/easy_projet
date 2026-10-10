

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.contact import CONTACT_DICTIONARY
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
    CONTACT_DICTIONARY,
)


CONTACT_ENTITY_DEFINITION = EntityDefinition(
    CONTACT_DICTIONARY,
)


CONTACT_LIST_DEFINITION = ListDefinition(
    identifier="contacts",
    entity=CONTACT_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "last_name"
            ),
            order=10,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "first_name"
            ),
            order=20,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "email"
            ),
            order=30,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "phone"
            ),
            order=40,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "client"
            ),
            order=50,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "employment_type"
            ),
            order=60,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "client_administration"
            ),
            order=70,
        ),
        ColumnDefinition(
            field=CONTACT_ENTITY_DEFINITION.get_field(
                "user_is_active"
            ),
            order=80,
        ),
    ),
    default_sort="last_name",
    page_size=DEFAULT_PAGE_SIZE,
)


ListValidator().validate(
    CONTACT_LIST_DEFINITION,
)