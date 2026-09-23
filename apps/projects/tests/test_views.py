

from django.test import TestCase, override_settings
from django.urls import reverse
from datetime import date

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import (
    Project,
    ProjectExternalParticipant,
    ProjectMembership,
)
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class ProjectViewTests(TestCase):
    """
    Tests d'intégration des vues de formulaire Projet.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société et environnement client
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test projets",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company,
            email="project-admin@example.com",
            first_name="Jean",
            last_name="Administrateur",
            is_system_admin=True,
        )

        cls.participant_user = User.objects.create(
            company=cls.company,
            email="project-participant@example.com",
            first_name="Paul",
            last_name="Participant",
        )

        cls.new_participant_user = User.objects.create(
            company=cls.company,
            email="project-new-participant@example.com",
            first_name="Marie",
            last_name="Nouvelle",
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut projet",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
            is_default=True,
        )

        # --------------------------------------------------------------
        # Rôles projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle sur projet",
        )

        cls.project_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.project_role_2 = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Niveau d'accès projet
        # --------------------------------------------------------------

        cls.project_access_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès au projet",
        )

        cls.project_access = CatalogValue.objects.create(
            catalog_type=cls.project_access_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
            is_default=True,
        )

        # --------------------------------------------------------------
        # Niveau d'accès participant externe
        # --------------------------------------------------------------

        cls.external_access_type = CatalogType.objects.create(
            code="PROJECT_EXTERNAL_ACCESS",
            label="Accès participant externe",
        )

        cls.external_access = CatalogValue.objects.create(
            catalog_type=cls.external_access_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
            is_default=True,
        )

        cls.external_access_2 = CatalogValue.objects.create(
            catalog_type=cls.external_access_type,
            code="EXTENDED",
            label="Étendu",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-TEST-001",
            name="Projet test vues",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Participant interne existant
        # --------------------------------------------------------------

        cls.membership = ProjectMembership.objects.create(
            project=cls.project,
            user=cls.participant_user,
            role=cls.project_role,
            access_level=cls.project_access,
        )

        # --------------------------------------------------------------
        # Participant externe existant
        # --------------------------------------------------------------

        cls.external_participant = (
            ProjectExternalParticipant.objects.create(
                project=cls.project,
                last_name="DUPONT",
                first_name="Pierre",
                email="pierre.dupont@example.com",
                company_name="Entreprise externe",
                access_level=cls.external_access,
            )
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------

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
            "projects:update",
            kwargs={
                "pk": self.project.pk,
            },
        )

    def build_project_data(self):
        """
        Construit les données principales du ProjectForm.

        Les deux formsets sont ajoutés séparément par les tests.
        """

        return {
            "reference": self.project.reference,
            "name": self.project.name,
            "description": self.project.description,
            "company": str(self.company.pk),
            "status": str(self.project_status.pk),
            "is_active": "on",
            "owner_company": "",
            "designer_company": "",
            "project_type": "",
            "contract_reference": "",
            "comments": "",
            "address_1": "",
            "address_2": "",
            "address_3": "",
            "postal_code": "",
            "city": "",
            "country": "",
            "planned_workload_hours": "0",
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "initial_receipt_date": "",
            "receipt_date": "",
            "initial_delivery_date": "",
            "delivery_date": "",
            "amount_quote_ht": "0.00",
            "amount_quote_ttc": "0.00",
            "amount_order_ht": "0.00",
            "amount_order_ttc": "0.00",
            "currency": "EUR",
            "budget_comments": "",
        }

    def add_empty_membership_formset(self, data):
        data.update(
            {
                "memberships-TOTAL_FORMS": "0",
                "memberships-INITIAL_FORMS": "0",
                "memberships-MIN_NUM_FORMS": "0",
                "memberships-MAX_NUM_FORMS": "1000",
            }
        )

    def add_empty_external_formset(self, data):
        data.update(
            {
                "external_participants-TOTAL_FORMS": "0",
                "external_participants-INITIAL_FORMS": "0",
                "external_participants-MIN_NUM_FORMS": "0",
                "external_participants-MAX_NUM_FORMS": "1000",
            }
        )

    # --------------------------------------------------------------
    # GET - Création
    # --------------------------------------------------------------

    def test_create_page_returns_200(self):
        response = self.client.get(
            reverse("projects:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_create_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            reverse("projects:create")
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_create_page_contains_memberships_collection(self):
        response = self.client.get(
            reverse("projects:create")
        )

        collection = self.get_collection(
            response,
            "memberships",
        )

        self.assertEqual(
            collection.name,
            "memberships",
        )

    def test_create_page_contains_external_participants_collection(
        self,
    ):
        response = self.client.get(
            reverse("projects:create")
        )

        collection = self.get_collection(
            response,
            "external_participants",
        )

        self.assertEqual(
            collection.name,
            "external_participants",
        )

    def test_create_page_renders_management_forms(self):
        response = self.client.get(
            reverse("projects:create")
        )

        self.assertContains(
            response,
            'name="memberships-TOTAL_FORMS"',
        )

        self.assertContains(
            response,
            'name="external_participants-TOTAL_FORMS"',
        )

    # --------------------------------------------------------------
    # GET - Modification
    # --------------------------------------------------------------

    def test_update_page_returns_200(self):
        response = self.client.get(
            self.get_update_url()
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context[
                "form_view"
            ].is_readonly,
        )

    def test_update_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            self.get_update_url()
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_update_page_contains_existing_membership(self):
        response = self.client.get(
            self.get_update_url()
        )

        collection = self.get_collection(
            response,
            "memberships",
        )

        self.assertEqual(
            len(collection.rows),
            1,
        )

        self.assertEqual(
            collection.rows[0]
            .django_form
            .instance,
            self.membership,
        )

    def test_update_page_contains_existing_external_participant(
        self,
    ):
        response = self.client.get(
            self.get_update_url()
        )

        collection = self.get_collection(
            response,
            "external_participants",
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

    # --------------------------------------------------------------
    # POST - Participant interne
    # --------------------------------------------------------------

    def test_update_adds_internal_participant(self):
        data = self.build_project_data()

        data.update(
            {
                "memberships-TOTAL_FORMS": "2",
                "memberships-INITIAL_FORMS": "1",
                "memberships-MIN_NUM_FORMS": "0",
                "memberships-MAX_NUM_FORMS": "1000",

                "memberships-0-id": str(
                    self.membership.pk
                ),
                "memberships-0-user": str(
                    self.participant_user.pk
                ),
                "memberships-0-role": str(
                    self.project_role.pk
                ),
                "memberships-0-access_level": str(
                    self.project_access.pk
                ),
                "memberships-0-is_active": "on",

                "memberships-1-id": "",
                "memberships-1-user": str(
                    self.new_participant_user.pk
                ),
                "memberships-1-role": str(
                    self.project_role.pk
                ),
                "memberships-1-access_level": str(
                    self.project_access.pk
                ),
                "memberships-1-is_active": "on",
            }
        )

        self.add_empty_external_formset(data)

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            ProjectMembership.objects.filter(
                project=self.project,
                user=self.new_participant_user,
                role=self.project_role,
                access_level=self.project_access,
            ).exists()
        )

    def test_update_modifies_internal_participant(self):
        data = self.build_project_data()

        data.update(
            {
                "memberships-TOTAL_FORMS": "1",
                "memberships-INITIAL_FORMS": "1",
                "memberships-MIN_NUM_FORMS": "0",
                "memberships-MAX_NUM_FORMS": "1000",

                "memberships-0-id": str(
                    self.membership.pk
                ),
                "memberships-0-user": str(
                    self.participant_user.pk
                ),
                "memberships-0-role": str(
                    self.project_role_2.pk
                ),
                "memberships-0-access_level": str(
                    self.project_access.pk
                ),
                "memberships-0-is_active": "on",
            }
        )

        self.add_empty_external_formset(data)

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.membership.refresh_from_db()

        self.assertEqual(
            self.membership.role,
            self.project_role_2,
        )

        self.assertEqual(
            self.membership.access_level,
            self.project_access,
        )

    def test_update_deletes_internal_participant(self):
        data = self.build_project_data()

        data.update(
            {
                "memberships-TOTAL_FORMS": "1",
                "memberships-INITIAL_FORMS": "1",
                "memberships-MIN_NUM_FORMS": "0",
                "memberships-MAX_NUM_FORMS": "1000",

                "memberships-0-id": str(
                    self.membership.pk
                ),
                "memberships-0-user": str(
                    self.participant_user.pk
                ),
                "memberships-0-role": str(
                    self.project_role.pk
                ),
                "memberships-0-access_level": str(
                    self.project_access.pk
                ),
                "memberships-0-is_active": "on",
                "memberships-0-DELETE": "on",
            }
        )

        self.add_empty_external_formset(data)

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            ProjectMembership.objects.filter(
                pk=self.membership.pk,
            ).exists()
        )

    # --------------------------------------------------------------
    # POST - Participant externe
    # --------------------------------------------------------------

    def test_update_adds_external_participant(self):
        data = self.build_project_data()

        self.add_empty_membership_formset(data)

        data.update(
            {
                "external_participants-TOTAL_FORMS": "2",
                "external_participants-INITIAL_FORMS": "1",
                "external_participants-MIN_NUM_FORMS": "0",
                "external_participants-MAX_NUM_FORMS": "1000",

                "external_participants-0-id": str(
                    self.external_participant.pk
                ),
                "external_participants-0-last_name": (
                    self.external_participant.last_name
                ),
                "external_participants-0-first_name": (
                    self.external_participant.first_name
                ),
                "external_participants-0-email": (
                    self.external_participant.email
                ),
                "external_participants-0-company_name": (
                    self.external_participant.company_name
                ),
                "external_participants-0-access_level": str(
                    self.external_access.pk
                ),
                "external_participants-0-is_active": "on",

                "external_participants-1-id": "",
                "external_participants-1-last_name": "MARTIN",
                "external_participants-1-first_name": "Julie",
                "external_participants-1-email": (
                    "julie.martin@example.com"
                ),
                "external_participants-1-company_name": (
                    "Nouvelle entreprise"
                ),
                "external_participants-1-access_level": str(
                    self.external_access.pk
                ),
                "external_participants-1-is_active": "on",
            }
        )

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            ProjectExternalParticipant.objects.filter(
                project=self.project,
                email="julie.martin@example.com",
            ).exists()
        )

    def test_update_modifies_external_participant(self):
        data = self.build_project_data()

        self.add_empty_membership_formset(data)

        data.update(
            {
                "external_participants-TOTAL_FORMS": "1",
                "external_participants-INITIAL_FORMS": "1",
                "external_participants-MIN_NUM_FORMS": "0",
                "external_participants-MAX_NUM_FORMS": "1000",

                "external_participants-0-id": str(
                    self.external_participant.pk
                ),
                "external_participants-0-last_name": (
                    self.external_participant.last_name
                ),
                "external_participants-0-first_name": (
                    self.external_participant.first_name
                ),
                "external_participants-0-email": (
                    self.external_participant.email
                ),
                "external_participants-0-company_name": (
                    "Société modifiée"
                ),
                "external_participants-0-access_level": str(
                    self.external_access_2.pk
                ),
                "external_participants-0-is_active": "on",
            }
        )

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.external_participant.refresh_from_db()

        self.assertEqual(
            self.external_participant.company_name,
            "Société modifiée",
        )

        self.assertEqual(
            self.external_participant.access_level,
            self.external_access_2,
        )

    def test_update_deletes_external_participant(self):
        data = self.build_project_data()

        self.add_empty_membership_formset(data)

        data.update(
            {
                "external_participants-TOTAL_FORMS": "1",
                "external_participants-INITIAL_FORMS": "1",
                "external_participants-MIN_NUM_FORMS": "0",
                "external_participants-MAX_NUM_FORMS": "1000",

                "external_participants-0-id": str(
                    self.external_participant.pk
                ),
                "external_participants-0-last_name": (
                    self.external_participant.last_name
                ),
                "external_participants-0-first_name": (
                    self.external_participant.first_name
                ),
                "external_participants-0-email": (
                    self.external_participant.email
                ),
                "external_participants-0-company_name": (
                    self.external_participant.company_name
                ),
                "external_participants-0-access_level": str(
                    self.external_access.pk
                ),
                "external_participants-0-is_active": "on",
                "external_participants-0-DELETE": "on",
            }
        )

        response = self.client.post(
            self.get_update_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            ProjectExternalParticipant.objects.filter(
                pk=self.external_participant.pk,
            ).exists()
        )

    def test_create_saves_and_displays_distinct_planning_dates(
        self,
    ):
        data = self.build_project_data()

        data.update(
            {
                "reference": "PRJ-TEST-DATES",
                "name": "Projet dates",
                "initial_start_date": "2026-01-10",
                "initial_end_date": "2026-01-20",
                "start_date": "2026-01-11",
                "end_date": "2026-01-19",
            }
        )

        self.add_empty_membership_formset(data)
        self.add_empty_external_formset(data)

        response = self.client.post(
            reverse("projects:create"),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        project = Project.objects.get(
            reference="PRJ-TEST-DATES",
        )

        self.assertEqual(
            project.initial_start_date,
            date(2026, 1, 10),
        )
        self.assertEqual(
            project.initial_end_date,
            date(2026, 1, 20),
        )
        self.assertEqual(
            project.start_date,
            date(2026, 1, 11),
        )
        self.assertEqual(
            project.end_date,
            date(2026, 1, 19),
        )

        response = self.client.get(
            reverse(
                "projects:update",
                kwargs={
                    "pk": project.pk,
                },
            )
        )

        self.assertContains(
            response,
            'value="2026-01-10"',
        )
        self.assertContains(
            response,
            'value="2026-01-20"',
        )
        self.assertContains(
            response,
            'value="2026-01-11"',
        )
        self.assertContains(
            response,
            'value="2026-01-19"',
        )

    def test_workspace_displays_effective_project_dates(
        self,
    ):
        Project.objects.filter(
            pk=self.project.pk,
        ).update(
            initial_start_date=date(2026, 1, 10),
            initial_end_date=date(2026, 1, 20),
            start_date=date(2026, 1, 11),
            end_date=date(2026, 1, 19),
        )

        response = self.client.get(
            reverse(
                "projects:workspace",
                kwargs={
                    "pk": self.project.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "11/01/2026",
        )
        self.assertContains(
            response,
            "19/01/2026",
        )