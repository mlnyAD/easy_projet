

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


DOCUMENT_PROPERTIES_FORM_DEFINITION = FormDefinition(
    name="document-properties",
    title="Propriétés du document",
    sections=[
        SectionDefinition(
            title="Informations générales",
            fields=[
                FieldDefinition(
                    name="title",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="description",
                    width=FieldWidth.MD,
                    required=False,
                ),
            ],
        ),
        SectionDefinition(
            title="Classement",
            fields=[
                FieldDefinition(
                    name="document_type",
                    width=FieldWidth.SM,
                    required=False,
                ),
                FieldDefinition(
                    name="status",
                    width=FieldWidth.SM,
                    required=False,
                ),
                FieldDefinition(
                    name="is_doe",
                    width=FieldWidth.SM,
                    required=False,
                    checked_label="Inclus au DOE",
                    unchecked_label="Non inclus au DOE",
                ),
            ],
        ),
        SectionDefinition(
            title="Données techniques",
            fields=[
                FieldDefinition(
                    name="folder_path",
                    width=FieldWidth.MD,
                    required=False,
                ),
                FieldDefinition(
                    name="original_filename",
                    width=FieldWidth.MD,
                    required=False,
                ),
                FieldDefinition(
                    name="technical_type",
                    width=FieldWidth.SM,
                    required=False,
                ),
                FieldDefinition(
                    name="version_number",
                    width=FieldWidth.SM,
                    required=False,
                ),
            ],
        ),
    ],
)