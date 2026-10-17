

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.form.collection import (
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
)
from framework.types.field_width import FieldWidth


TODO_ACTION_FORM_DEFINITION = FormDefinition(
    name="todo-action",
    title="Nouvelle action",
    sections=[
        SectionDefinition(
            title="Action",
            fields=[
                FieldDefinition(
                    name="title",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="details",
                    width=FieldWidth.MD,
                    required=False,
                ),
                FieldDefinition(
                    name="due_date",
                    width=FieldWidth.SM,
                    required=False,
                ),
                FieldDefinition(
                    name="origin",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="project",
                    width=FieldWidth.MD,
                    required=False,
                ),
            ],
        ),
    ],
    collections=[
        FormCollectionDefinition(
            name="recipients",
            title="Destinataires",
            description=(
                "Indiquez les personnes concernées "
                "et leur rôle dans l'action."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="user",
                    label="Destinataire",
                    field_name="user",
                ),
                FormCollectionColumnDefinition(
                    name="role",
                    label="Rôle",
                    field_name="role",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un destinataire",
            delete_label="Retirer le destinataire",
        ),
    ],
)