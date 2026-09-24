from django.test import TestCase
from django.utils import timezone

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.meetings.models import Meeting, MeetingParticipant
from apps.meetings.services.invitations import MeetingInvitationService
from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


class MeetingInvitationServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Société réunions")
        ClientEnvironment.objects.create(company=cls.company)

        cls.author = User.objects.create(
            company=cls.company,
            email="author@example.com",
            first_name="Alice",
            last_name="Auteur",
        )
        cls.participant = User.objects.create(
            company=cls.company,
            email="participant@example.com",
            first_name="Paul",
            last_name="Participant",
        )

        project_status_type = CatalogType.objects.create(
            code="TEST_INVITATION_PROJECT_STATUS",
            label="Statut projet",
        )
        project_status = CatalogValue.objects.create(
            catalog_type=project_status_type,
            code="ACTIVE",
            label="Actif",
        )
        meeting_status_type = CatalogType.objects.create(
            code="MEETING_STATUS",
            label="Statut réunion",
        )
        meeting_status = CatalogValue.objects.create(
            catalog_type=meeting_status_type,
            code="PLANNED",
            label="Planifiée",
        )
        role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle projet",
        )
        role = CatalogValue.objects.create(
            catalog_type=role_type,
            code="USER",
            label="Utilisateur",
        )
        access_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès",
        )
        access = CatalogValue.objects.create(
            catalog_type=access_type,
            code="STANDARD",
            label="Standard",
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-INVITATION",
            name="Projet invitations",
            status=project_status,
        )
        for user in (cls.author, cls.participant):
            ProjectMembership.objects.create(
                project=cls.project,
                user=user,
                role=role,
                access_level=access,
            )

        cls.meeting = Meeting.objects.create(
            project=cls.project,
            organizer=cls.author,
            status=meeting_status,
            subject="Réunion de préparation",
            scheduled_at=timezone.now(),
        )

    def test_internal_invitation_marks_meeting_as_sent(self):
        MeetingParticipant.objects.create(
            meeting=self.meeting,
            participant=self.participant,
        )

        result = MeetingInvitationService.send(
            meeting=self.meeting,
            author=self.author,
        )

        self.assertFalse(result.email_failed)

        self.meeting.refresh_from_db()
        self.assertTrue(self.meeting.invitations_sent)
