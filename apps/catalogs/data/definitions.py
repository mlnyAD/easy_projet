

from .models import CatalogDefinition

CATALOG_DEFINITIONS = [

    CatalogDefinition(
        code="ACTIVITY_REPORT",
        label="Rapport d'activité",
    ),

    CatalogDefinition(
        code="ACTIVITY_REPORT_LINE",
        label="Détail rapport d'activité",
        is_incremental=True,
        is_editable=True,
    ),

    CatalogDefinition(
        code="DOCUMENT_TYPE",
        label="Type de document",
        is_incremental=True,
        is_editable=True,
    ),

    CatalogDefinition(
        code="DOCUMENT_STATUS",
        label="Statut d'un document",
    ),

    CatalogDefinition(
        code="LICENSE_STATUS",
        label="Statut de la licence",
    ),

    CatalogDefinition(
        code="MEETING_STATUS",
        label="Statut d'une réunion",
    ),

    CatalogDefinition(
        code="PROJECT_STATUS",
        label="Statut du projet",
    ),

    CatalogDefinition(
        code="PROJECT_TYPE",
        label="Type de projet",
    ),

    CatalogDefinition(
        code="RISK_CLASS",
        label="Type de risque",
    ),

    CatalogDefinition(
        code="RISK_GRAVITY",
        label="Gravité du risque",
    ),

    CatalogDefinition(
        code="RISK_IMPACT",
        label="Impact du risque",
    ),

    CatalogDefinition(
        code="RISK_ORIGIN",
        label="Origine du risque",
    ),

    CatalogDefinition(
        code="RISK_PROBABILITY",
        label="Probabilité d'apparition du risque",
    ),

    CatalogDefinition(
        code="RISK_STATE",
        label="Etat du risque",
    ),

    CatalogDefinition(
        code="RISK_TYPE",
        label="Type de risque",
    ),

    CatalogDefinition(
        code="TASK_STATUS",
        label="Statut de la tâche",
    ),

    CatalogDefinition(
        code="USER_EMPLOYMENT_TYPE",
        label="Type d'emploi de l'utilisateur",
    ),

    CatalogDefinition(
        code="USER_JOB",
        label="Métier de l'utilisateur",
        is_incremental=True,
        is_editable=True,
    ),

    CatalogDefinition(
        code="USER_LEVEL_ACCESS",
        label="Niveau accès de l'utilisateur",
    ),

    CatalogDefinition(
        code="USER_GLOBAL_ROLE",
        label="Rôle de l'utilisateur",
    ),

    CatalogDefinition(
        code="USER_PROJECT_ROLE",
        label="Rôle de l'utilisateur sur le projet",
    ),

    CatalogDefinition(
        code="USER_TEAM_ROLE",
        label="Rôle de l'utilisateur dans l'équipe",
    ),

    CatalogDefinition(
        code="WORK_PACKAGE_STATUS",
        label="Statut du lot de travaux",
    ),

]