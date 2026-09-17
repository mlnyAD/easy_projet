

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.client_environment_membership import (
    CLIENT_ENVIRONMENT_MEMBERSHIP_DICTIONARY,
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
    CLIENT_ENVIRONMENT_MEMBERSHIP_DICTIONARY
)

CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION = (
    EntityDefinition(
        CLIENT_ENVIRONMENT_MEMBERSHIP_DICTIONARY
    )
)

CLIENT_ENVIRONMENT_MEMBERSHIP_LIST_DEFINITION = (
    ListDefinition(
        entity=(
            CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
        ),
        columns=(
            ColumnDefinition(
                field=(
                    CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
                    .get_field("client_environment")
                ),
                order=10,
            ),
            ColumnDefinition(
                field=(
                    CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
                    .get_field("employment_type")
                ),
                order=20,
            ),
            ColumnDefinition(
                field=(
                    CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
                    .get_field("is_client_admin")
                ),
                order=30,
            ),
            ColumnDefinition(
                field=(
                    CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
                    .get_field(
                        "is_client_admin_responsible"
                    )
                ),
                order=40,
            ),
            ColumnDefinition(
                field=(
                    CLIENT_ENVIRONMENT_MEMBERSHIP_ENTITY_DEFINITION
                    .get_field("is_active")
                ),
                order=50,
            ),
        ),
        default_sort="client_environment",
        page_size=DEFAULT_PAGE_SIZE,
    )
)

ListValidator().validate(
    CLIENT_ENVIRONMENT_MEMBERSHIP_LIST_DEFINITION
)