

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.risks.models import Risk
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class RiskAccessTests(TestCase):
    """
    Tests de cloisonnement des risques par projet accessible.

    L'utilisateur est affecté uniquement au projet A.
    Il ne doit ni voir ni modifier les risques du projet B.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Risques",
        )

        cls.environment_a = (
            ClientEnvironment.objects.create(
                company=cls.company_a,
            )
        )

        cls.company_b = Company.objects.create(
            name="Société B - Risques",
        )

        cls.environment_b = (
            ClientEnvironment.objects.create(
                company=cls.company_b,
            )
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_RISK_GLOBAL_ROLE",
            label="Rôle global test risques",
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_RISK_ACCESS_LEVEL",
            label="Niveau accès test risques",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateur connecté
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company_a,
            email="risk-user@example.com",
            first_name="Jean",
            last_name="Risque",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Rôle projet
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

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_RISK_PROJECT_STATUS",
            label="Statut projet test",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Projets A et B
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-RISK-A",
            name="Projet risques A",
            status=cls.project_status,
        )

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-RISK-B",
            name="Projet risques B",
            status=cls.project_status,
        )

        # L'utilisateur n'est affecté qu'au projet A.

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.user,
            role=cls.project_role,
        )

        # --------------------------------------------------------------
        # Catalogues Risk
        # --------------------------------------------------------------

        cls.origin = cls.create_catalog_value(
            catalog_code="RISK_ORIGIN",
            value_code="INTERNAL",
            label="Interne",
        )

        cls.risk_type = cls.create_catalog_value(
            catalog_code="RISK_TYPE",
            value_code="RISK",
            label="Risque",
        )

        cls.risk_class = cls.create_catalog_value(
            catalog_code="RISK_CLASS",
            value_code="TECHNICAL",
            label="Technique",
        )

        cls.impact = cls.create_catalog_value(
            catalog_code="RISK_IMPACT",
            value_code="COST",
            label="Coût",
        )

        cls.severity = cls.create_catalog_value(
            catalog_code="RISK_GRAVITY",
            value_code="MEDIUM",
            label="Moyenne",
        )

        cls.probability = cls.create_catalog_value(
            catalog_code="RISK_PROBABILITY",
            value_code="MEDIUM",
            label="Moyenne",
        )

        cls.status = cls.create_catalog_value(
            catalog_code="RISK_STATE",
            value_code="ACTIVE",
            label="Actif",
        )

        cls.criticality = cls.create_catalog_value(
            catalog_code="RISK_CRITICALITY",
            value_code="MEDIUM",
            label="Moyenne",
        )

        cls.review_frequency = cls.create_catalog_value(
            catalog_code="RISK_REVIEW_FREQUENCY",
            value_code="MONTHLY",
            label="Mensuelle",
        )

        # --------------------------------------------------------------
        # Risques
        # --------------------------------------------------------------

        cls.risk_a = cls.create_risk(
            project=cls.project_a,
            title="Risque accessible A",
        )

        cls.risk_b = cls.create_risk(
            project=cls.project_b,
            title="Risque inaccessible B",
        )

    @classmethod
    def create_catalog_value(
        cls,
        *,
        catalog_code,
        value_code,
        label,
    ):
        catalog_type = CatalogType.objects.create(
            code=catalog_code,
            label=catalog_code,
        )

        return CatalogValue.objects.create(
            catalog_type=catalog_type,
            code=value_code,
            label=label,
            sort_order=10,
        )

    @classmethod
    def create_risk(
        cls,
        *,
        project,
        title,
    ):
        return Risk.objects.create(
            project=project,
            origin=cls.origin,
            risk_type=cls.risk_type,
            risk_class=cls.risk_class,
            impact=cls.impact,
            severity=cls.severity,
            probability=cls.probability,
            status=cls.status,
            criticality=cls.criticality,
            review_frequency=cls.review_frequency,
            title=title,
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def build_post_data(
        self,
        *,
        project,
        risk=None,
        title="Risque formulaire",
    ):
        return {
            "project": str(project.pk),
            "owner": "",
            "origin": str(self.origin.pk),
            "risk_type": str(self.risk_type.pk),
            "risk_class": str(self.risk_class.pk),
            "impact": str(self.impact.pk),
            "severity": str(self.severity.pk),
            "probability": str(self.probability.pk),
            "status": str(self.status.pk),
            "criticality": str(self.criticality.pk),
            "review_frequency": str(
                self.review_frequency.pk
            ),
            "reference": (
                risk.reference
                if risk is not None
                else ""
            ),
            "title": title,
            "description": "",
            "occurrence_date": "",
            "closure_date": "",
            "estimated_cost": "",
            "last_review_date": "",
            "planned_actions": "",
            "is_active": "on",
        }

    # ------------------------------------------------------------------
    # Liste globale
    # ------------------------------------------------------------------

    def test_global_list_only_contains_accessible_risks(self):
        response = self.client.get(
            reverse(
                "risks:list",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.risk_a.title,
        )

        self.assertNotContains(
            response,
            self.risk_b.title,
        )

    # ------------------------------------------------------------------
    # Liste par projet
    # ------------------------------------------------------------------

    def test_accessible_project_list_returns_200(self):
        response = self.client.get(
            reverse(
                "risks:list-by-project",
                kwargs={
                    "project_pk": self.project_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_inaccessible_project_list_returns_404(self):
        response = self.client.get(
            reverse(
                "risks:list-by-project",
                kwargs={
                    "project_pk": self.project_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_form_only_contains_accessible_projects(self):
        response = self.client.get(
            reverse(
                "risks:create",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        form = response.context["form"]

        project_ids = set(
            form.fields[
                "project"
            ]
            .queryset
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.project_a.pk,
            project_ids,
        )

        self.assertNotIn(
            self.project_b.pk,
            project_ids,
        )

    def test_create_with_accessible_project_succeeds(self):
        response = self.client.post(
            reverse(
                "risks:create",
            ),
            data=self.build_post_data(
                project=self.project_a,
                title="Nouveau risque A",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Risk.objects.filter(
                project=self.project_a,
                title="Nouveau risque A",
            ).exists()
        )

    def test_create_with_inaccessible_project_is_rejected(self):
        initial_count = (
            Risk.objects
            .filter(
                project=self.project_b,
            )
            .count()
        )

        response = self.client.post(
            reverse(
                "risks:create",
            ),
            data=self.build_post_data(
                project=self.project_b,
                title="Tentative risque B",
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Risk.objects
            .filter(
                project=self.project_b,
            )
            .count(),
            initial_count,
        )

    # ------------------------------------------------------------------
    # Modification
    # ------------------------------------------------------------------

    def test_accessible_risk_update_returns_200(self):
        response = self.client.get(
            reverse(
                "risks:update",
                kwargs={
                    "pk": self.risk_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_inaccessible_risk_update_returns_404(self):
        response = self.client.get(
            reverse(
                "risks:update",
                kwargs={
                    "pk": self.risk_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_cannot_move_risk_to_inaccessible_project(self):
        response = self.client.post(
            reverse(
                "risks:update",
                kwargs={
                    "pk": self.risk_a.pk,
                },
            ),
            data=self.build_post_data(
                project=self.project_b,
                risk=self.risk_a,
                title=self.risk_a.title,
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.risk_a.refresh_from_db()

        self.assertEqual(
            self.risk_a.project_id,
            self.project_a.pk,
        )