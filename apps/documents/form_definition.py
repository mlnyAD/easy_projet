

from common.constants.document import (
    DOCUMENT_IMPORT_MAX_FILES,
)
from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.form.file_upload import (
    FileUploadDefinition,
)
from framework.form.kinds import FieldKind
from framework.types.field_width import FieldWidth


DOCUMENT_IMPORT_FORM_DEFINITION = FormDefinition(
    name="document-import",
    title="Importer des fichiers",
    sections=[
        SectionDefinition(
            title="Fichiers",
            fields=[
                FieldDefinition(
                    name="files",
                    label=(
                        "Fichiers à importer "
                        "(50 maximum)"
                    ),
                    help_text=(
                        "Sélectionnez au plus 50 fichiers "
                        "par import."
                    ),
                    kind=FieldKind.FILE_UPLOAD,
                    width=FieldWidth.MD,
                    upload=FileUploadDefinition(
                        multiple=True,
                        max_files=DOCUMENT_IMPORT_MAX_FILES,
                        preview=False,
                        allow_replace=False,
                        allow_delete=False,
                    ),
                ),
            ],
        ),
        SectionDefinition(
            title="Classement",
            fields=[
                FieldDefinition(
                    name="description",
                    width=FieldWidth.MD,
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
    ],
)


DOCUMENT_CREATE_FORM_DEFINITION = FormDefinition(
    name="document-create",
    title="Nouveau document",
    sections=[
        SectionDefinition(
            title="Informations générales",
            fields=[
                FieldDefinition(
                    name="title",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="document_format",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="folder",
                    width=FieldWidth.MD,
                ),
            ],
        ),
        SectionDefinition(
            title="Classement",
            fields=[
                FieldDefinition(
                    name="document_type",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="status",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="lifecycle",
                    width=FieldWidth.SM,
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
    ],
)


DOCUMENT_SIGNATURE_REQUEST_FORM_DEFINITION = FormDefinition(
    name="document-signature-request",
    title="Demande de signature",
    sections=[
        SectionDefinition(
            title="Demande",
            fields=[
                FieldDefinition(
                    name="title",
                    width=FieldWidth.MD,
                ),
            ],
        ),
        SectionDefinition(
            title="Documents à signer",
            fields=[
                FieldDefinition(
                    name="documents",
                    width=FieldWidth.FULL,
                    help_text=(
                        "Seuls les documents PDF peuvent être "
                        "envoyés en signature."
                    ),
                ),
            ],
        ),
        SectionDefinition(
            title="Signataires",
            fields=[
                FieldDefinition(
                    name="internal_signers",
                    width=FieldWidth.FULL,
                    required=False,
                ),
                FieldDefinition(
                    name="external_signers",
                    width=FieldWidth.FULL,
                    required=False,
                ),
            ],
        ),
    ],
)


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