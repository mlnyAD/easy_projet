

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
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="first_name",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.SM,
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
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="phone",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="mobile",
                    width=FieldWidth.XS,
                ),
            ],
        ),

        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="company",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="job",
                    width=FieldWidth.XS,
                ),
            ],
        ),

        SectionDefinition(
            title="Droits système",
            fields=[
                FieldDefinition(
                    name="is_system_admin",
                    required=False,
                    width=FieldWidth.XS,
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