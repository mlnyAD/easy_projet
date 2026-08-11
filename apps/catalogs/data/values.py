

from .models import CatalogValueDefinition

CATALOG_VALUE_DEFINITIONS = [

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT",
        code="COMPLETED",
        label="Renseigné",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT",
        code="VALID",
        label="Validé",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="WORK",
        label="Travail",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="ABSENCE",
        label="Absence",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="URGENCY",
        label="Urgence",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="WEATHER",
        label="Météo",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="WAITING",
        label="En attente",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="TRAINING",
        label="En formation",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="ACTIVITY_REPORT_LINE",
        code="OTHER",
        label="Autre",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_TYPE",
        code="CR_REUNION",
        label="CR de réunion",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_TYPE",
        code="NOTE_TECHNIQUE",
        label="Note technique",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_TYPE",
        code="PHOTO",
        label="Photo",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_TYPE",
        code="PLAN",
        label="Plan",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_TYPE",
        code="RAPPORT_VISITE",
        label="Rapport de visite",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="TO_BE_DRAFTED",
        label="A rédiger",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="IN_PROGRESS",
        label="En cours",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="PENDING_VALIDATION",
        label="A valider",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="VALIDATED",
        label="Validé",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="ABANDONNED",
        label="Abandonné",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="DELETED",
        label="Supprimé",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="DOCUMENT_STATUS",
        code="OBSOLETE",
        label="Obsolète",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="LICENSE_STATUS",
        code="ACTIVE",
        label="Active",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="LICENSE_STATUS",
        code="WAITING",
        label="En attente",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="LICENSE_STATUS",
        code="EXPIRED",
        label="Expirée",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="MEETING_STATUS",
        code="PLANNED",
        label="Planifiée",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="MEETING_STATUS",
        code="COMPLETED",
        label="Terminée",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="MEETING_STATUS",
        code="CANCELLED",
        label="Annulée",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="PLANNED",
        label="Planifié",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="IN_PROGRESS",
        label="En cours",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="SUSPENDED",
        label="Suspendu",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="COMPLETED",
        label="Terminé",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="IN_VALIDATION",
        label="En validation",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="ARCHIVED",
        label="Archivé",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_STATUS",
        code="CANCELED",
        label="Annulé",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_TYPE",
        code="NEW_CONSTRUCTION",
        label="Neuf",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_TYPE",
        code="RENOVATION",
        label="Rénovation",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_TYPE",
        code="REPAIR",
        label="Réparation",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="PROJECT_TYPE",
        code="MAINTENANCE",
        label="Entretien",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="SCHEDULING",
        label="Planning",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="COMPANY",
        label="Entreprise",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="LEGAL",
        label="Juridique",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="ORGANIZATION",
        label="Organisation",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="PROJECT",
        label="Projet",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="TECHNICAL",
        label="Technique",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="HUMAN_RESOURCES",
        label="Humain",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="DEADLINES",
        label="Délais",
        sort_order=80,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="SUBCONTRACTING",
        label="Sous-traitance",
        sort_order=90,
    ),

    CatalogValueDefinition(
        catalog="RISK_CLASS",
        code="OTHER",
        label="Autre",
        sort_order=100,
    ),
    
    CatalogValueDefinition(
        catalog="RISK_CRITICALITY",
        code="LOW",
        label="Faible",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_CRITICALITY",
        code="MEDIUM",
        label="Moyenne",
        sort_order=20,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="RISK_CRITICALITY",
        code="HIGH",
        label="Élevée",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_CRITICALITY",
        code="CRITICAL",
        label="Critique",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_GRAVITY",
        code="MINOR",
        label="Mineur",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_GRAVITY",
        code="SIGNIFICANT",
        label="Significatif",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_GRAVITY",
        code="CRITICAL",
        label="Critique",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_GRAVITY",
        code="CATASTROPHIC",
        label="Catastrophique",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_IMPACT",
        code="COST",
        label="Coût",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_IMPACT",
        code="TIME_LINE",
        label="Délais",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_IMPACT",
        code="REALIZATION",
        label="Réalisation",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_IMPACT",
        code="QUALITY",
        label="Qualité",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_ORIGIN",
        code="INTERNAL",
        label="Interne",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_ORIGIN",
        code="EXTERNAL",
        label="Externe",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_ORIGIN",
        code="MIXTE",
        label="Mixte",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_PROBABILITY",
        code="VERY_UNLIKELY",
        label="Très peu probable",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_PROBABILITY",
        code="UNLIKELY",
        label="Peu probable",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_PROBABILITY",
        code="LIKELY",
        label="Probable",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_PROBABILITY",
        code="VERY_LIKELY",
        label="Très probable",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_REVIEW_FREQUENCY",
        code="WEEKLY",
        label="Hebdomadaire",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="RISK_REVIEW_FREQUENCY",
        code="MONTHLY",
        label="Mensuelle",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_REVIEW_FREQUENCY",
        code="ON_EVENT",
        label="À chaque événement",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_STATE",
        code="LATENT",
        label="Latent",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_STATE",
        code="EMERGED",
        label="Apparu",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="RISK_STATE",
        code="ACTIVE",
        label="Actif",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="RISK_STATE",
        code="EXTINCT",
        label="Eteint",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="RISK_TYPE",
        code="RISK",
        label="Risque",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="RISK_TYPE",
        code="OPPORTUNITY",
        label="Opportunité",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="TASK_STATUS",
        code="PLANNED",
        label="Planifiée",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="TASK_STATUS",
        code="IN_PROGRESS",
        label="En cours",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="TASK_STATUS",
        code="SUSPENDED",
        label="Suspendue",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="TASK_STATUS",
        code="DONE",
        label="Terminée",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="TASK_STATUS",
        code="CANCELLED",
        label="Annulée",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="USER_EMPLOYMENT_TYPE",
        code="EMPLOYEE",
        label="Employé",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="USER_EMPLOYMENT_TYPE",
        code="SUBCONTRACTOR",
        label="Sous-traitant",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="USER_EMPLOYMENT_TYPE",
        code="EXTERNAL",
        label="Externe",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="USER_JOB",
        code="PLUMBER",
        label="Plombier",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="USER_JOB",
        code="MASON",
        label="Maçon",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="USER_JOB",
        code="ELECTRICIAN",
        label="Electricien",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="USER_LEVEL_ACCESS",
        code="ADMIN",
        label="Administrateur",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="USER_LEVEL_ACCESS",
        code="STANDARD",
        label="Standard",
        sort_order=20,
         is_default=True,
    ),

    CatalogValueDefinition(
        catalog="USER_LEVEL_ACCESS",
        code="READ_ONLY",
        label="Lecture seule",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="USER_GLOBAL_ROLE",
        code="SYSTEM_ADMIN",
        label="Administrateur système",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="USER_GLOBAL_ROLE",
        code="CLIENT_ADMIN",
        label="Administrateur client",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="USER_GLOBAL_ROLE",
        code="NONE",
        label="Aucun",
        sort_order=30,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="USER_PROJECT_ROLE",
        code="PROJECT_MANAGER",
        label="Chef de projet",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="USER_PROJECT_ROLE",
        code="USER",
        label="Utilisateur",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="USER_TEAM_ROLE",
        code="TEAM_LEADER",
        label="Chef d'équipe",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="USER_TEAM_ROLE",
        code="COMPANION",
        label="Companion",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="USER_TEAM_ROLE",
        code="NONE",
        label="Aucun",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="WORK_PACKAGE_STATUS",
        code="PLANNED",
        label="Planifié",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="WORK_PACKAGE_STATUS",
        code="IN_PROGRESS",
        label="En cours",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="WORK_PACKAGE_STATUS",
        code="SUSPENDED",
        label="Suspendu",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="WORK_PACKAGE_STATUS",
        code="DONE",
        label="Terminé",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="WORK_PACKAGE_STATUS",
        code="CANCELLED",
        label="Annulé",
        sort_order=50,
    ),
    
    # ========================================================================
    # Intégrations - Types de service
    # ========================================================================

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="MEETING",
        label="Réunions et visioconférence",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="EMAIL",
        label="Messagerie électronique",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="DOCUMENT_STORAGE",
        label="Gestion documentaire",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="SIGNATURE",
        label="Signature électronique",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="MESSAGING",
        label="Messagerie instantanée",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="CAD_VIEWER",
        label="Visualisation CAO",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="WORKFLOW",
        label="Workflow",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="OFFICE",
        label="Suite bureautique",
        sort_order=80,
    ),
    
    CatalogValueDefinition(
        catalog="INTEGRATION_SERVICE_TYPE",
        code="MAPPING",
        label="Cartographie et géolocalisation",
        sort_order=90,
    ),

    # ========================================================================
    # Intégrations - Fournisseurs
    # ========================================================================

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="MICROSOFT_365",
        label="Microsoft 365",
        sort_order=10,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="GOOGLE_WORKSPACE",
        label="Google Workspace",
        sort_order=20,
    ),
    
    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="GOOGLE_MAPS",
        label="Google Maps",
        sort_order=25,
    ), 

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="SMTP",
        label="Serveur SMTP",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="SHAREPOINT",
        label="Microsoft SharePoint",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="NEXTCLOUD",
        label="Nextcloud",
        sort_order=50,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="DOCUSEAL",
        label="DocuSeal",
        sort_order=60,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="COLLABORA",
        label="Collabora Online",
        sort_order=70,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="ONLYOFFICE",
        label="ONLYOFFICE",
        sort_order=80,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_PROVIDER",
        code="CADVIEWER",
        label="CADViewer",
        sort_order=90,
    ),

    # ========================================================================
    # Intégrations - État de connexion
    # ========================================================================

    CatalogValueDefinition(
        catalog="INTEGRATION_CONNECTION_STATUS",
        code="NOT_CONFIGURED",
        label="Non configurée",
        sort_order=10,
        is_default=True,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_CONNECTION_STATUS",
        code="CONFIGURED",
        label="Configurée",
        sort_order=20,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_CONNECTION_STATUS",
        code="CONNECTED",
        label="Connectée",
        sort_order=30,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_CONNECTION_STATUS",
        code="ERROR",
        label="Erreur",
        sort_order=40,
    ),

    CatalogValueDefinition(
        catalog="INTEGRATION_CONNECTION_STATUS",
        code="DISABLED",
        label="Désactivée",
        sort_order=50,
    ),    
    
]