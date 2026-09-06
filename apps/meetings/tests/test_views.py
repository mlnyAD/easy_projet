

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.meetings.models import (
    Meeting,
    MeetingParticipant,
)
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class MeetingViewTests(TestCase):
    """
    Tests d'intégration des vues de formulaire Réunion.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test réunions",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_MEETING_USER_ROLE",
            label="Rôle global test réunions",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_MEETING_ACCESS_LEVEL",
            label="Niveau accès test réunions",
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
            email="meeting-view@example.com",
            first_name="Jean",
            last_name="Réunion",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.participant_user = User.objects.create(
            company=cls.company,
            email="meeting-participant@example.com",
            first_name="Paul",
            last_name="Participant",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_MEETING_PROJECT_STATUS",
            label="Statut projet test réunions",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.meeting_status_type = CatalogType.objects.create(
            code="MEETING_STATUS",
            label="Statut réunion",
        )

        cls.meeting_status = CatalogValue.objects.create(
            catalog_type=cls.meeting_status_type,
            code="PLANNED",
            label="Planifiée",
            sort_order=10,
            is_default=True,
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-MEETING-001",
            name="Projet test réunions",
            status=cls.project_status,
        )
        cls.project_role_type = (
            CatalogType.objects.create(
                code="USER_PROJECT_ROLE",
                label="Rôle projet",
            )
        )

        cls.project_role = (
            CatalogValue.objects.create(
                catalog_type=cls.project_role_type,
                code="USER",
                label="Utilisateur",
                sort_order=10,
            )
        )

        cls.project_membership = (
            ProjectMembership.objects.create(
                project=cls.project,
                user=cls.user,
                role=cls.project_role,
            )
        )
            
        cls.meeting = Meeting.objects.create(
            project=cls.project,
            organizer=cls.user,
            status=cls.meeting_status,
            subject="Réunion de test",
            scheduled_at=timezone.now(),
        )

        cls.internal_participant = (
            MeetingParticipant.objects.create(
                meeting=cls.meeting,
                participant=cls.participant_user,
            )
        )

        cls.external_participant = (
            MeetingParticipant.objects.create(
                meeting=cls.meeting,
                external_email="external@example.com",
            )
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_collection(
        self,
        response,
        name,
    ):
        for collection in (
            response.context[
                "form_view"
            ].collections
        ):
            if collection.name == name:
                return collection

        self.fail(
            f"Collection {name!r} introuvable."
        )

    def get_update_url(self):
        return reverse(
            "meetings:update",
            kwargs={
                "pk": self.meeting.pk,
            },
        )

    def build_update_post_data(self):
        """
        Construit un POST valide représentant l'état courant
        de la réunion et de ses deux collections.
        """

        return {
            # Réunion
            "project": str(
                self.project.pk
            ),
            "organizer": str(
                self.user.pk
            ),
            "status": str(
                self.meeting_status.pk
            ),
            "reference": self.meeting.reference,
            "subject": self.meeting.subject,
            "scheduled_at": (
                self.meeting.scheduled_at
                .strftime("%Y-%m-%dT%H:%M")
            ),
            "duration_hours": (
                self.meeting.duration_hours
                or ""
            ),
            "location": self.meeting.location,
            "agenda": self.meeting.agenda,
            "notes": self.meeting.notes,
            "comments": self.meeting.comments,
            "is_active": "on",

            # Participants internes
            "internal-TOTAL_FORMS": "1",
            "internal-INITIAL_FORMS": "1",
            "internal-MIN_NUM_FORMS": "0",
            "internal-MAX_NUM_FORMS": "1000",

            "internal-0-id": str(
                self.internal_participant.pk
            ),
            "internal-0-meeting": str(
                self.meeting.pk
            ),
            "internal-0-participant": str(
                self.participant_user.pk
            ),

            # Participants externes
            "external-TOTAL_FORMS": "1",
            "external-INITIAL_FORMS": "1",
            "external-MIN_NUM_FORMS": "0",
            "external-MAX_NUM_FORMS": "1000",

            "external-0-id": str(
                self.external_participant.pk
            ),
            "external-0-meeting": str(
                self.meeting.pk
            ),
            "external-0-external_email": (
                self.external_participant.external_email
            ),
        }

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_page_returns_200(self):
        response = self.client.get(
            reverse(
                "meetings:create",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_create_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            reverse(
                "meetings:create",
            )
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_create_page_contains_internal_collection(self):
        response = self.client.get(
            reverse(
                "meetings:create",
            )
        )

        collection = self.get_collection(
            response,
            "internal",
        )

        self.assertEqual(
            collection.name,
            "internal",
        )

    def test_create_page_contains_external_collection(self):
        response = self.client.get(
            reverse(
                "meetings:create",
            )
        )

        collection = self.get_collection(
            response,
            "external",
        )

        self.assertEqual(
            collection.name,
            "external",
        )

    def test_create_page_renders_management_forms(self):
        response = self.client.get(
            reverse(
                "meetings:create",
            )
        )

        self.assertContains(
            response,
            'name="internal-TOTAL_FORMS"',
        )

        self.assertContains(
            response,
            'name="external-TOTAL_FORMS"',
        )

    # ------------------------------------------------------------------
    # Modification - affichage
    # ------------------------------------------------------------------

    def test_update_page_returns_200(self):
        response = self.client.get(
            self.get_update_url()
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_update_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            self.get_update_url()
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_update_page_contains_internal_participant(self):
        response = self.client.get(
            self.get_update_url()
        )

        collection = self.get_collection(
            response,
            "internal",
        )

        self.assertEqual(
            len(collection.rows),
            1,
        )

        self.assertEqual(
            collection.rows[0]
            .django_form
            .instance,
            self.internal_participant,
        )

    def test_update_page_contains_external_participant(self):
        response = self.client.get(
            self.get_update_url()
        )

        collection = self.get_collection(
            response,
            "external",
        )

        self.assertEqual(
            len(collection.rows),
            1,
        )

        self.assertEqual(
            collection.rows[0]
            .django_form
            .instance,
            self.external_participant,
        )

    # ------------------------------------------------------------------
    # Modification - participants internes
    # ------------------------------------------------------------------

    def test_update_can_add_internal_participant(self):
        new_participant = User.objects.create(
            company=self.company,
            email="meeting-new-participant@example.com",
            first_name="Luc",
            last_name="Nouveau",
            global_role=self.global_role,
            access_level=self.access_level,
        )

        data = self.build_update_post_data()

        data.update(
            {
                "internal-TOTAL_FORMS": "2",

                "internal-1-id": "",
                "internal-1-meeting": str(
                    self.meeting.pk
                ),
                "internal-1-participant": str(
                    new_participant.pk
                ),
            }
        )

        response = self.client.post(
            self.get_update_url(),
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            MeetingParticipant.objects.filter(
                meeting=self.meeting,
                participant=new_participant,
            ).exists()
        )

    def test_update_can_delete_internal_participant(self):
        data = self.build_update_post_data()

        data["internal-0-DELETE"] = "on"

        response = self.client.post(
            self.get_update_url(),
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            MeetingParticipant.objects.filter(
                pk=self.internal_participant.pk,
            ).exists()
        )

        self.assertTrue(
            MeetingParticipant.objects.filter(
                pk=self.external_participant.pk,
            ).exists()
        )

    # ------------------------------------------------------------------
    # Modification - participants externes
    # ------------------------------------------------------------------

    def test_update_can_add_external_participant(self):
        data = self.build_update_post_data()

        data.update(
            {
                "external-TOTAL_FORMS": "2",

                "external-1-id": "",
                "external-1-meeting": str(
                    self.meeting.pk
                ),
                "external-1-external_email": (
                    "NEW.EXTERNAL@EXAMPLE.COM"
                ),
            }
        )

        response = self.client.post(
            self.get_update_url(),
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        participant = (
            MeetingParticipant.objects.get(
                meeting=self.meeting,
                external_email=(
                    "new.external@example.com"
                ),
            )
        )

        self.assertTrue(
            participant.is_external
        )

    def test_update_can_delete_external_participant(self):
        data = self.build_update_post_data()

        data["external-0-DELETE"] = "on"

        response = self.client.post(
            self.get_update_url(),
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            MeetingParticipant.objects.filter(
                pk=self.external_participant.pk,
            ).exists()
        )

        self.assertTrue(
            MeetingParticipant.objects.filter(
                pk=self.internal_participant.pk,
            ).exists()
        )