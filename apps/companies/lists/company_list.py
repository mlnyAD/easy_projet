

from framework.dictionary import (
    DictionaryValidator,
    EntityDefinition,
)
from framework.list import (
    ColumnDefinition,
    ListDefinition,
    ListValidator,
)


COMPANY_DICTIONARY = {
    "entity": {
        "name": "company",
        "label": "Société",
        "label_plural": "Sociétés",
        "description": "Société cliente ou intervenante d'Easy Projet.",
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "required": True,
            "unique": True,
        },
        "name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": 150,
        },
        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": True,
            "max_length": 254,
        },
        "phone": {
            "label": "Téléphone",
            "data_type": "phone",
            "max_length": 20,
        },
        "address_1": {
            "label": "Adresse",
            "data_type": "string",
            "max_length": 100,
        },
        "address_2": {
            "label": "Complément d'adresse",
            "data_type": "string",
            "max_length": 100,
        },
        "address_3": {
            "label": "Complément d'adresse 2",
            "data_type": "string",
            "max_length": 100,
        },
        "postal_code": {
            "label": "Code postal",
            "data_type": "postal_code",
            "max_length": 10,
        },
        "city": {
            "label": "Ville",
            "data_type": "string",
            "max_length": 50,
        },
        "country": {
            "label": "Pays",
            "data_type": "country",
            "max_length": 50,
        },
        "is_active": {
            "label": "Active",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },
        "created_at": {
            "label": "Créée le",
            "data_type": "datetime",
            "required": True,
        },
        "updated_at": {
            "label": "Modifiée le",
            "data_type": "datetime",
            "required": True,
        },
    },
}


DictionaryValidator().validate(COMPANY_DICTIONARY)

COMPANY_ENTITY_DEFINITION = EntityDefinition(
    COMPANY_DICTIONARY
)


COMPANY_LIST_DEFINITION = ListDefinition(
    entity=COMPANY_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("name"),
            order=10,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("email"),
            order=20,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("phone"),
            order=30,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("city"),
            order=40,
        ),
        ColumnDefinition(
            field=COMPANY_ENTITY_DEFINITION.get_field("is_active"),
            order=50,
        ),
    ),
    default_sort="name",
    page_size=20,
)


ListValidator().validate(COMPANY_LIST_DEFINITION)