

from framework.form import (
    FieldDefinition,
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


USER_FORM_DEFINITION = FormDefinition(
    name="user",
    title="Utilisateur",

    sections=[
        SectionDefinition(
            title="Identité",
            fields=[
                FieldDefinition(
                    name="last_name",
                ),
                FieldDefinition(
                    name="first_name",
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.FULL,
                    checked_label="Actif",
                    unchecked_label="Inactif",
                ),
            ],
        ),

        SectionDefinition(
            title="Coordonnées",
            fields=[
                FieldDefinition(
                    name="email",
                ),
                FieldDefinition(
                    name="phone",
                ),
                FieldDefinition(
                    name="mobile",
                ),
            ],
        ),

        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="company",
                ),
                FieldDefinition(
                    name="job",
                ),
            ],
        ),

        SectionDefinition(
            title="Droits système",
            fields=[
                FieldDefinition(
                    name="is_system_admin",
                    required=False,
                    width=FieldWidth.FULL,
                    checked_label=(
                        "Administrateur système"
                    ),
                    unchecked_label=(
                        "Utilisateur standard"
                    ),
                ),
            ],
        ),
    ],

    collections=[
        FormCollectionDefinition(
            name="client_environments",
            title="Environnements clients",
            description=(
                "Seules les sociétés disposant d'une "
                "licence sont proposées."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="client_environment",
                    label="Environnement client",
                    field_name="client_environment",
                ),
                FormCollectionColumnDefinition(
                    name="employment_type",
                    label="Type d'emploi",
                    field_name="employment_type",
                ),
                FormCollectionColumnDefinition(
                    name="is_active",
                    label="Rattachement actif",
                    field_name="is_active",
                ),
                FormCollectionColumnDefinition(
                    name=(
                        "is_client_admin_responsible"
                    ),
                    label=(
                        "Administrateur client titulaire"
                    ),
                    field_name=(
                        "is_client_admin_responsible"
                    ),
                ),
                FormCollectionColumnDefinition(
                    name="is_client_admin_delegate",
                    label=(
                        "Administrateur client délégué"
                    ),
                    field_name=(
                        "is_client_admin_delegate"
                    ),
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un environnement client",
            delete_label="Supprimer le rattachement",
        ),
    ],
)