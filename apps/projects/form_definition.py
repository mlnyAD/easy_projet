

from framework.form import (
    FieldDefinition,
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


PROJECT_FORM_DEFINITION = FormDefinition(
    name="project",
    title="Projet",
    sections=[
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="reference",
                ),
                FieldDefinition(
                    name="name",
                ),
                FieldDefinition(
                    name="description",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="company",
                ),
                FieldDefinition(
                    name="project_manager",
                ),
                FieldDefinition(
                    name="status",
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
            title="Client et contrat",
            fields=[
                FieldDefinition(
                    name="owner_company",
                ),
                FieldDefinition(
                    name="designer_company",
                ),
                FieldDefinition(
                    name="project_type",
                ),
                FieldDefinition(
                    name="contract_reference",
                ),
                FieldDefinition(
                    name="comments",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Localisation",
            fields=[
                FieldDefinition(
                    name="address_1",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="address_2",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="address_3",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="postal_code",
                ),
                FieldDefinition(
                    name="city",
                ),
                FieldDefinition(
                    name="country",
                ),
            ],
        ),
        SectionDefinition(
            title="Charge et planning",
            fields=[
                FieldDefinition(
                    name="planned_workload_hours",
                ),
                FieldDefinition(
                    name="initial_start_date",
                ),
                FieldDefinition(
                    name="initial_end_date",
                ),
                FieldDefinition(
                    name="start_date",
                ),
                FieldDefinition(
                    name="end_date",
                ),
                FieldDefinition(
                    name="initial_receipt_date",
                ),
                FieldDefinition(
                    name="receipt_date",
                ),
                FieldDefinition(
                    name="initial_delivery_date",
                ),
                FieldDefinition(
                    name="delivery_date",
                ),
            ],
        ),
        SectionDefinition(
            title="Données commerciales",
            fields=[
                FieldDefinition(
                    name="amount_quote_ht",
                ),
                FieldDefinition(
                    name="amount_quote_ttc",
                ),
                FieldDefinition(
                    name="amount_order_ht",
                ),
                FieldDefinition(
                    name="amount_order_ttc",
                ),
                FieldDefinition(
                    name="currency",
                ),
                FieldDefinition(
                    name="budget_comments",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
    ],
    collections=[
        FormCollectionDefinition(
            name="memberships",
            title="Participants internes",
            description=(
                "Utilisateurs Easy Projet affectés au projet."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="user",
                    label="Utilisateur",
                    field_name="user",
                ),
                FormCollectionColumnDefinition(
                    name="role",
                    label="Rôle sur le projet",
                    field_name="role",
                ),
                FormCollectionColumnDefinition(
                    name="is_active",
                    label="Actif",
                    field_name="is_active",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un participant",
            delete_label="Supprimer le participant",
        ),
        FormCollectionDefinition(
            name="external_participants",
            title="Participants externes",
            description=(
                "Intervenants ponctuels ne disposant pas "
                "nécessairement d'un compte Easy Projet."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="last_name",
                    label="Nom",
                    field_name="last_name",
                ),
                FormCollectionColumnDefinition(
                    name="first_name",
                    label="Prénom",
                    field_name="first_name",
                ),
                FormCollectionColumnDefinition(
                    name="email",
                    label="Adresse électronique",
                    field_name="email",
                ),
                FormCollectionColumnDefinition(
                    name="company_name",
                    label="Société",
                    field_name="company_name",
                ),
                FormCollectionColumnDefinition(
                    name="access_level",
                    label="Niveau d'accès",
                    field_name="access_level",
                ),
                FormCollectionColumnDefinition(
                    name="is_active",
                    label="Actif",
                    field_name="is_active",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un participant externe",
            delete_label="Supprimer le participant externe",
        ),
    ],
)