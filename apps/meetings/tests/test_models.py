

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.meetings.models import (
    Meeting,
    MeetingParticipant,
)
from apps.projects.models import Project
from apps.users.models import User


class MeetingModelTests(TestCase):
    """
    Tests métier des modèles Réunion et Participant.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test modèles réunions",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_MEETING_MODEL_USER_ROLE",
            label="Rôle global test",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_MEETING_MODEL_ACCESS",
            label="Niveau accès test",
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="meeting-model@example.com",
            first_name="Jean",
            last_name="Modèle",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.participant_user = User.objects.create(
            company=cls.company,
            email="participant-model@example.com",
            first_name="Paul",
            last_name="Participant",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_MEETING_PROJECT_STATUS",
            label="Statut projet test",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.meeting_status_type = CatalogType.objects.create(
            code="TEST_MEETING_MODEL_STATUS",
            label="Statut réunion test",
        )

        cls.meeting_status = CatalogValue.objects.create(
            catalog_type=cls.meeting_status_type,
            code="PLANNED",
            label="Planifiée",
            sort_order=10,
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-MEETING-MODEL",
            name="Projet test modèles réunions",
            status=cls.project_status,
        )

    def create_meeting(
        self,
        **kwargs,
    ):
        data = {
            "project": self.project,
            "organizer": self.user,
            "status": self.meeting_status,
            "subject": "Réunion de test",
            "scheduled_at": timezone.now(),
        }
        data.update(kwargs)

        return Meeting.objects.create(
            **data
        )

    def test_reference_is_generated_automatically(self):
        meeting = self.create_meeting()

        self.assertTrue(
            meeting.reference
        )

    def test_reference_sequence_increments(self):
        first = self.create_meeting(
            subject="Première réunion",
        )

        second = self.create_meeting(
            subject="Deuxième réunion",
        )

        self.assertNotEqual(
            first.reference,
            second.reference,
        )

        first_number = int(
            first.reference.rsplit("_", 1)[1]
        )
        second_number = int(
            second.reference.rsplit("_", 1)[1]
        )

        self.assertEqual(
            second_number,
            first_number + 1,
        )

    def test_meeting_text_fields_are_trimmed_on_save(self):
        meeting = self.create_meeting(
            subject="  Réunion test  ",
            location="  Salle A  ",
            agenda="  Point principal  ",
            notes="  Note participant  ",
            comments="  Commentaire interne  ",
        )

        self.assertEqual(
            meeting.subject,
            "Réunion test",
        )
        self.assertEqual(
            meeting.location,
            "Salle A",
        )
        self.assertEqual(
            meeting.agenda,
            "Point principal",
        )
        self.assertEqual(
            meeting.notes,
            "Note participant",
        )
        self.assertEqual(
            meeting.comments,
            "Commentaire interne",
        )

    def test_duration_must_be_positive(self):
        meeting = Meeting(
            project=self.project,
            organizer=self.user,
            status=self.meeting_status,
            subject="Réunion durée invalide",
            scheduled_at=timezone.now(),
            duration_hours=Decimal("-1.00"),
        )

        with self.assertRaises(
            ValidationError
        ):
            meeting.full_clean()

    def test_internal_participant_is_not_external(self):
        meeting = self.create_meeting()

        participant = MeetingParticipant.objects.create(
            meeting=meeting,
            participant=self.participant_user,
        )

        self.assertFalse(
            participant.is_external
        )

        self.assertEqual(
            participant.display_name,
            str(self.participant_user),
        )

    def test_external_participant_is_external(self):
        meeting = self.create_meeting()

        participant = MeetingParticipant.objects.create(
            meeting=meeting,
            external_email="external@example.com",
        )

        self.assertTrue(
            participant.is_external
        )

        self.assertEqual(
            participant.display_name,
            "external@example.com",
        )

    def test_participant_cannot_be_internal_and_external(self):
        meeting = self.create_meeting()

        participant = MeetingParticipant(
            meeting=meeting,
            participant=self.participant_user,
            external_email="external@example.com",
        )

        with self.assertRaises(
            ValidationError
        ):
            participant.full_clean()

    def test_external_participant_requires_identity(self):
        meeting = self.create_meeting()

        participant = MeetingParticipant(
            meeting=meeting,
        )

        with self.assertRaises(
            ValidationError
        ):
            participant.full_clean()