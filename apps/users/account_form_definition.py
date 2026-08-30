

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.form.file_upload import (
    FileUploadDefinition,
)
from framework.form.kinds import FieldKind
from framework.types.field_width import (
    FieldWidth,
)


ACCOUNT_FORM_DEFINITION = FormDefinition(
    name="account",
    title="Mon compte",
    sections=[
        SectionDefinition(
            title="Identité",
            fields=[
                FieldDefinition(
                    name="photo",
                    kind=FieldKind.FILE_UPLOAD,
                    required=False,
                    width=FieldWidth.FULL,
                    upload=FileUploadDefinition(
                        multiple=False,
                        allowed_extensions=(
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".webp",
                        ),
                        allowed_mime_types=(
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                        ),
                        max_files=1,
                        preview=True,
                        allow_replace=True,
                        allow_delete=True,
                    ),
                ),
                FieldDefinition(
                    name="first_name"
                ),
                FieldDefinition(
                    name="last_name"
                ),
                FieldDefinition(
                    name="email"
                ),
                FieldDefinition(
                    name="company_display"
                ),
                FieldDefinition(
                    name="global_role_display"
                ),
            ],
        ),
        SectionDefinition(
            title="Sécurité",
            fields=[
                FieldDefinition(
                    name="current_password",
                    required=False,
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="new_password",
                    required=False,
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name=(
                        "new_password_confirmation"
                    ),
                    required=False,
                    width=FieldWidth.FULL,
                ),
            ],
        ),
    ],
)