

from common.constants import DEFAULT_PAGE_SIZE
from common.dictionaries.integration import (
    EXTERNAL_INTEGRATION_DICTIONARY,
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
    EXTERNAL_INTEGRATION_DICTIONARY
)


EXTERNAL_INTEGRATION_ENTITY_DEFINITION = EntityDefinition(
    EXTERNAL_INTEGRATION_DICTIONARY
)


EXTERNAL_INTEGRATION_LIST_DEFINITION = ListDefinition(
    entity=EXTERNAL_INTEGRATION_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("client_environment")
            ),
            label="Client",
            width="md",
            truncate=True,
            order=10,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("service_type")
            ),
            label="Service",
            width="md",
            truncate=True,
            order=20,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("provider")
            ),
            label="Fournisseur",
            width="md",
            truncate=True,
            order=30,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("name")
            ),
            label="Nom",
            width="lg",
            truncate=True,
            order=40,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("connection_status")
            ),
            label="Connexion",
            width="sm",
            order=50,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("priority")
            ),
            label="Priorité",
            width="xs",
            align="center",
            order=60,
        ),
        ColumnDefinition(
            field=(
                EXTERNAL_INTEGRATION_ENTITY_DEFINITION
                .get_field("is_active")
            ),
            label="Active",
            width="xs",
            align="center",
            order=70,
        ),
    ),
    default_sort="priority",
    page_size=DEFAULT_PAGE_SIZE,
)


ListValidator().validate(
    EXTERNAL_INTEGRATION_LIST_DEFINITION
)