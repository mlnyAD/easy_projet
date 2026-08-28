

from framework.form import (
    FieldDefinition,
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


TASK_FORM_DEFINITION = FormDefinition(
    name="task",
    title="Tâche",
    sections=[
        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="work_package",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="status",
                ),
            ],
        ),
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="name",
                ),
                FieldDefinition(
                    name="description",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.FULL,
                    checked_label="Active",
                    unchecked_label="Inactive",
                ),
            ],
        ),
        SectionDefinition(
            title="Planning",
            fields=[
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
                    name="planned_workload_hours",
                ),
                FieldDefinition(
                    name="remaining_workload_hours",
                ),
                FieldDefinition(
                    name="progress_percent",
                ),
            ],
        ),
    ],
    collections=[
        FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="user",
                    label="Utilisateur",
                    field_name="user",
                ),
                FormCollectionColumnDefinition(
                    name="role",
                    label="Rôle",
                    field_name="role",
                ),
                FormCollectionColumnDefinition(
                    name="allocation_percent",
                    label="Taux de charge (%)",
                    field_name="allocation_percent",
                ),
                FormCollectionColumnDefinition(
                    name="is_active",
                    label="Actif",
                    field_name="is_active",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter une personne",
            delete_label="Supprimer l'affectation",
        ),
        FormCollectionDefinition(
            name="dependencies",
            title="Enchaînements",
            columns=(
                FormCollectionColumnDefinition(
                    name="predecessor",
                    label="Tâche antécédente",
                    field_name="predecessor",
                ),
                FormCollectionColumnDefinition(
                    name="dependency_type",
                    label="Type",
                    field_name="dependency_type",
                ),
                FormCollectionColumnDefinition(
                    name="lag_days",
                    label="Décalage (jours)",
                    field_name="lag_days",
                ),
                FormCollectionColumnDefinition(
                    name="is_active",
                    label="Actif",
                    field_name="is_active",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un enchaînement",
            delete_label="Supprimer l'enchaînement",
        ),
    ],  
)