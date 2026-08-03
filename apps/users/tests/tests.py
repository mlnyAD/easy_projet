

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company

from apps.users.forms import UserForm


User = get_user_model()


class UserTestDataMixin:
    @classmethod
    def setUpTestData(cls) -> None:
        cls.company = Company.objects.create(
            name="Société active",
            is_active=True,
        )
        cls.inactive_company = Company.objects.create(
            name="Société inactive",
            is_active=False,
        )

        cls.employment_type_catalog = CatalogType.objects.create(
            code="USER_EMPLOYMENT_TYPE",
            label="Types d'emploi",
            is_active=True,
        )
        cls.job_catalog = CatalogType.objects.create(
            code="USER_JOB",
            label="Métiers",
            is_active=True,
        )
        cls.global_role_catalog = CatalogType.objects.create(
            code="USER_GLOBAL_ROLE",
            label="Rôles globaux",
            is_active=True,
        )
        cls.access_level_catalog = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveaux d'accès",
            is_active=True,
        )

        cls.employment_type = CatalogValue.objects.create(
            catalog_type=cls.employment_type_catalog,
            code="EMPLOYEE",
            label="Salarié",
            is_active=True,
        )
        cls.job = CatalogValue.objects.create(
            catalog_type=cls.job_catalog,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            is_active=True,
        )
        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_catalog,
            code="CLIENT_ADMIN",
            label="Administrateur client",
            is_active=True,
        )
        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_catalog,
            code="STANDARD",
            label="Standard",
            is_active=True,
        )

        cls.other_catalog = CatalogType.objects.create(
            code="OTHER_CATALOG",
            label="Autre catalogue",
            is_active=True,
        )
        cls.other_value = CatalogValue.objects.create(
            catalog_type=cls.other_catalog,
            code="OTHER",
            label="Autre valeur",
            is_active=True,
        )

    def make_form_data(
        self,
        **overrides,
    ) -> dict[str, object]:
        data: dict[str, object] = {
            "last_name": "DUPONT",
            "first_name": "Jean",
            "email": "jean.dupont@example.com",
            "phone": "01 23 45 67 89",
            "mobile": "06 12 34 56 78",
            "company": self.company.pk,
            "employment_type": self.employment_type.pk,
            "job": self.job.pk,
            "global_role": self.global_role.pk,
            "access_level": self.access_level.pk,
            "is_active": True,
            "theme": "light",
        }
        data.update(overrides)
        return data

    def create_user(
        self,
        *,
        email: str = "existing@example.com",
    ):
        user = User(
            last_name="MARTIN",
            first_name="Alice",
            email=email,
            company=self.company,
            employment_type=self.employment_type,
            job=self.job,
            global_role=self.global_role,
            access_level=self.access_level,
            is_active=True,
        )
        user.set_unusable_password()
        user.save()

        return user


class UserModelTests(
    UserTestDataMixin,
    TestCase,
):
    def test_user_normalizes_data_and_generates_initials(self):
        user = User(
            last_name="  martin  ",
            first_name="  alice  ",
            email="  ALICE.MARTIN@EXAMPLE.COM  ",
            company=self.company,
            global_role=self.global_role,
            access_level=self.access_level,
        )
        user.set_unusable_password()
        user.save()

        self.assertEqual(user.last_name, "martin")
        self.assertEqual(user.first_name, "alice")
        self.assertEqual(
            user.email,
            "alice.martin@example.com",
        )
        self.assertEqual(user.initials, "AM")

    def test_string_representation(self):
        user = self.create_user()

        self.assertEqual(
            str(user),
            "MARTIN Alice",
        )


class UserFormTests(
    UserTestDataMixin,
    TestCase,
):
    def test_valid_form_creates_user(self):
        form = UserForm(
            data=self.make_form_data(),
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save()

        self.assertEqual(
            user.email,
            "jean.dupont@example.com",
        )
        self.assertFalse(user.has_usable_password())

    def test_email_is_required(self):
        form = UserForm(
            data=self.make_form_data(email=""),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_must_be_unique(self):
        self.create_user(
            email="duplicate@example.com",
        )

        form = UserForm(
            data=self.make_form_data(
                email="duplicate@example.com",
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_only_active_companies_are_available(self):
        form = UserForm()

        company_queryset = form.fields["company"].queryset

        self.assertIn(
            self.company,
            company_queryset,
        )
        self.assertNotIn(
            self.inactive_company,
            company_queryset,
        )

    def test_catalog_fields_are_filtered(self):
        form = UserForm()

        self.assertIn(
            self.job,
            form.fields["job"].queryset,
        )
        self.assertNotIn(
            self.other_value,
            form.fields["job"].queryset,
        )

        self.assertIn(
            self.global_role,
            form.fields["global_role"].queryset,
        )
        self.assertNotIn(
            self.other_value,
            form.fields["global_role"].queryset,
        )

    def test_editing_user_does_not_change_password_state(self):
        user = self.create_user()
        self.assertFalse(user.has_usable_password())

        form = UserForm(
            data=self.make_form_data(
                email=user.email,
            ),
            instance=user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        updated_user = form.save()

        self.assertFalse(
            updated_user.has_usable_password(),
        )
        
    def test_catalog_fields_display_only_functional_label(self):
        form = UserForm()

        job_field = form.fields["job"]

        self.assertEqual(
            job_field.label_from_instance(self.job),
            "Chef de projet",
        )

        self.assertNotIn(
            "USER_JOB",
            job_field.label_from_instance(self.job),
        )
        
    def test_global_role_displays_only_functional_label(self):
        form = UserForm()

        field = form.fields["global_role"]

        self.assertEqual(
            field.label_from_instance(self.global_role),
            "Administrateur client",
        )
        
    def test_catalog_field_exposes_catalog_metadata(self):
        form = UserForm()

        field = form.fields["job"]

        self.assertEqual(
            field.catalog_code,
            "USER_JOB",
        )
        self.assertIsInstance(
            field.catalog_is_editable,
            bool,
        )
        self.assertIsInstance(
            field.catalog_is_incremental,
            bool,
        )

class UserViewTests(
    UserTestDataMixin,
    TestCase,
):
    def test_list_view_is_accessible(self):
        response = self.client.get(
            reverse("users:list"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "users/user_list.html",
        )
        self.assertIn("list_view", response.context)

    def test_create_view_is_accessible(self):
        response = self.client.get(
            reverse("users:create"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_create_view_creates_user(self):
        response = self.client.post(
            reverse("users:create"),
            data=self.make_form_data(),
        )

        self.assertRedirects(
            response,
            reverse("users:list"),
        )

        user = User.objects.get(
            email="jean.dupont@example.com",
        )

        self.assertFalse(user.has_usable_password())

    def test_update_view_modifies_user(self):
        user = self.create_user()

        response = self.client.post(
            reverse(
                "users:update",
                kwargs={"pk": user.pk},
            ),
            data=self.make_form_data(
                email=user.email,
                first_name="Élodie",
            ),
        )

        self.assertRedirects(
            response,
            reverse("users:list"),
        )

        user.refresh_from_db()

        self.assertEqual(user.first_name, "Élodie")

    def test_update_view_returns_404_for_unknown_user(self):
        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": "00000000-0000-0000-0000-000000000000",
                },
            ),
        )

        self.assertEqual(response.status_code, 404)