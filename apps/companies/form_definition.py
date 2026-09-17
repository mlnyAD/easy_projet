

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


COMPANY_FORM_DEFINITION = FormDefinition(
    name="company",
    title="Société",

    sections=[
        SectionDefinition(
            title="Informations générales",
            fields=[
                FieldDefinition(
                    name="name",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="logo",
                    kind=FieldKind.FILE_UPLOAD,
                    required=False,
                    width=FieldWidth.MD,
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
                    name="siret",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="vat_number",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.SM,
                    checked_label="Active",
                    unchecked_label="Inactive",
                ),
            ],
        ),
        SectionDefinition(
            title="Coordonnées",
            fields=[
                FieldDefinition(
                    name="email",
                    width=FieldWidth.LG,
                ),
                FieldDefinition(
                    name="phone",
                    width=FieldWidth.SM,
                ),
            ],
        ),
        SectionDefinition(
            title="Adresse",
            fields=[
                FieldDefinition(
                    name="address_1",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="address_2",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="address_3",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="postal_code",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="city",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="country",
                    width=FieldWidth.SM,
                ),
            ],
        ),
    ],
)