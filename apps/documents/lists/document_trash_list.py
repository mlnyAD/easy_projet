

from common.constants.common import DEFAULT_PAGE_SIZE
from common.constants.document import (
    DOCUMENT_FILENAME_LENGTH,
    DOCUMENT_TITLE_LENGTH,
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


DOCUMENT_TRASH_DICTIONARY = {
    "entity": {
        "name": "document_trash",
        "label": "Document dans la corbeille",
        "label_plural": "Documents dans la corbeille",
        "description": (
            "Projection de lecture des documents placés "
            "dans la corbeille d'un projet."
        ),
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },
        "title": {
            "label": "Document",
            "data_type": "string",
            "required": True,
            "max_length": DOCUMENT_TITLE_LENGTH,
        },
        "current_filename": {
            "label": "Fichier",
            "data_type": "string",
            "required": False,
            "generated": True,
            "max_length": DOCUMENT_FILENAME_LENGTH,
        },
        "folder_full_path": {
            "label": "Dossier d’origine",
            "data_type": "string",
            "required": True,
            "generated": True,
        },
        "trashed_at": {
            "label": "Mis à la corbeille",
            "data_type": "datetime",
            "required": True,
            "generated": True,
        },
        "trashed_by_display": {
            "label": "Par",
            "data_type": "string",
            "required": False,
            "generated": True,
        },
    },
}


DictionaryValidator().validate(DOCUMENT_TRASH_DICTIONARY)

_ENTITY_DEFINITION = EntityDefinition(DOCUMENT_TRASH_DICTIONARY)

DOCUMENT_TRASH_LIST_DEFINITION = ListDefinition(
    identifier="document-trash",
    entity=_ENTITY_DEFINITION,
    columns=(
        ColumnDefinition(
            field=_ENTITY_DEFINITION.get_field("title"),
            order=10,
            width="md",
            truncate=True,
        ),
        ColumnDefinition(
            field=_ENTITY_DEFINITION.get_field("current_filename"),
            order=20,
            width="lg",
            truncate=True,
            sortable=False,
        ),
        ColumnDefinition(
            field=_ENTITY_DEFINITION.get_field("folder_full_path"),
            order=30,
            width="lg",
            truncate=True,
            sortable=False,
        ),
        ColumnDefinition(
            field=_ENTITY_DEFINITION.get_field("trashed_at"),
            order=40,
            width="md",
        ),
        ColumnDefinition(
            field=_ENTITY_DEFINITION.get_field(
                "trashed_by_display"
            ),
            order=50,
            width="md",
            truncate=True,
            sortable=False,
        ),
    ),
    default_sort="trashed_at",
    page_size=DEFAULT_PAGE_SIZE,
)

ListValidator().validate(DOCUMENT_TRASH_LIST_DEFINITION)