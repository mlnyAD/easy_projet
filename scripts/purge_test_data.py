

"""
Purge des données métier de test Easy Projet.

Les catalogues, permissions, types de contenu et migrations
sont volontairement conservés.

Script temporaire de développement.
"""

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction

from apps.communications.models import (
    CommunicationConversation,
)
from apps.core.models import ClientEnvironment
from apps.documents.models import DocumentFolder
from apps.integrations.models import ExternalIntegration
from apps.licenses.models import License
from apps.meetings.models import Meeting
from apps.projects.models import Project
from apps.reporting.models import ActivityReport
from apps.risks.models import Risk
from apps.todos.models import TodoAction
from apps.work.models import WorkPackage

from apps.companies.models import Company


User = get_user_model()


@transaction.atomic
def purge() -> None:
    """
    Supprime les données métier de test.

    Les suppressions partent des racines métier ; les relations
    configurées avec CASCADE suppriment leurs descendants.
    """

    print("Purge des données métier...")

    # Données personnelles / transversales.
    TodoAction.objects.all().delete()
    ActivityReport.objects.all().delete()

    # Données projet.
    CommunicationConversation.objects.all().delete()
    DocumentFolder.objects.all().delete()
    Meeting.objects.all().delete()
    Risk.objects.all().delete()
    WorkPackage.objects.all().delete()
    Project.objects.all().delete()

    # Données d'environnement client.
    ExternalIntegration.objects.all().delete()
    License.objects.all().delete()

    # Données techniques liées aux utilisateurs.
    LogEntry.objects.all().delete()
    Session.objects.all().delete()

    # Identités.
    User.objects.all().delete()

    # Environnements et annuaire sociétés.
    ClientEnvironment.objects.all().delete()
    Company.objects.all().delete()

    print("Purge terminée.")


purge()