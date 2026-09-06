

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.test import TestCase, override_settings

from unittest.mock import patch

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.users.forms import UserForm
from apps.users.services import TemporaryPasswordService


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
        
        cls.admin_user = User.objects.create(
            last_name="ADMIN",
            first_name="Client",
            email="admin.client@example.com",
            company=cls.company,
            global_role=cls.global_role,
            access_level=cls.access_level,
            is_active=True,
        )

        cls.admin_user.set_password(
            "TestPassword123!"
        )

        cls.admin_user.save(
            update_fields=[
                "password",
                "updated_at",
            ]
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
            user=self.admin_user,
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
        form = UserForm(
            user=self.admin_user,
        )

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
            user=self.admin_user,
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
    def setUp(self) -> None:
        self.client.force_login(
            self.admin_user
        )
        
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

    @override_settings(
        EMAIL_BACKEND=(
            "django.core.mail.backends.locmem.EmailBackend"
        ),
        DEFAULT_FROM_EMAIL="noreply@easy-projet.test",
    )
    def test_create_view_creates_user(self):
        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="Abcdef12!xyz",
        ):
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

        self.assertTrue(
            user.has_usable_password()
        )

        self.assertTrue(
            user.check_password(
                "Abcdef12!xyz"
            )
        )

        self.assertTrue(
            user.must_change_password
        )

        self.assertIsNotNone(
            user.temporary_password_sent_at
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            [
                "jean.dupont@example.com",
            ],
        )

        self.assertIn(
            "Abcdef12!xyz",
            email.body,
        )
        
    @override_settings(
        EMAIL_BACKEND=(
            "django.core.mail.backends.locmem.EmailBackend"
        ),
    )
    def test_create_view_rolls_back_when_email_fails(self):
        with patch(
            (
                "apps.users.services."
                "temporary_password_service."
                "EmailMessage.send"
            ),
            side_effect=RuntimeError(
                "SMTP indisponible"
            ),
        ):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    reverse("users:create"),
                    data=self.make_form_data(),
                )

        self.assertFalse(
            User.objects.filter(
                email="jean.dupont@example.com",
            ).exists()
        )        
        
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
        
    @override_settings(
        EMAIL_BACKEND=(
            "django.core.mail.backends.locmem.EmailBackend"
        ),
        DEFAULT_FROM_EMAIL="noreply@easy-projet.test",
    )
    def test_resend_temporary_password(self):
        user = self.create_user(
            email="alice@example.com",
        )

        user.set_password(
            "OldPassword1!"
        )
        user.save()

        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="NewPassword2!",
        ):
            response = self.client.post(
                reverse(
                    "users:temporary-password-resend",
                    kwargs={
                        "pk": user.pk,
                    },
                )
            )

        self.assertRedirects(
            response,
            reverse("users:list"),
        )

        user.refresh_from_db()

        self.assertFalse(
            user.check_password(
                "OldPassword1!"
            )
        )

        self.assertTrue(
            user.check_password(
                "NewPassword2!"
            )
        )

        self.assertTrue(
            user.must_change_password
        )

        self.assertIsNotNone(
            user.temporary_password_sent_at
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].to,
            [
                "alice@example.com",
            ],
        )


    def test_resend_temporary_password_rejects_get(self):
        user = self.create_user()

        response = self.client.get(
            reverse(
                "users:temporary-password-resend",
                kwargs={
                    "pk": user.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )


    def test_resend_temporary_password_returns_404_for_unknown_user(
        self,
    ):
        response = self.client.post(
            reverse(
                "users:temporary-password-resend",
                kwargs={
                    "pk": (
                        "00000000-0000-0000-0000-000000000000"
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends.locmem.EmailBackend"
    ),
    DEFAULT_FROM_EMAIL="noreply@easy-projet.test",
)
class TemporaryPasswordServiceTests(
    UserTestDataMixin,
    TestCase,
):
    def test_generate_password_has_expected_length(self):
        password = (
            TemporaryPasswordService.generate_password()
        )

        self.assertEqual(
            len(password),
            12,
        )

    def test_generate_password_contains_required_characters(self):
        password = (
            TemporaryPasswordService.generate_password()
        )

        self.assertTrue(
            any(
                character.islower()
                for character in password
            )
        )

        self.assertTrue(
            any(
                character.isupper()
                for character in password
            )
        )

        self.assertTrue(
            any(
                character.isdigit()
                for character in password
            )
        )

        self.assertTrue(
            any(
                character
                in TemporaryPasswordService.SYMBOLS
                for character in password
            )
        )

    def test_reset_and_send_assigns_temporary_password(self):
        user = self.create_user()

        self.assertFalse(
            user.has_usable_password()
        )

        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="Abcdef12!xyz",
        ):
            TemporaryPasswordService.reset_and_send(
                user=user,
            )

        user.refresh_from_db()

        self.assertTrue(
            user.has_usable_password()
        )

        self.assertTrue(
            user.check_password(
                "Abcdef12!xyz"
            )
        )

        self.assertTrue(
            user.must_change_password
        )

        self.assertIsNotNone(
            user.temporary_password_sent_at
        )

    def test_reset_and_send_sends_email(self):
        user = self.create_user(
            email="alice@example.com",
        )

        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="Abcdef12!xyz",
        ):
            TemporaryPasswordService.reset_and_send(
                user=user,
            )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            [
                "alice@example.com",
            ],
        )

        self.assertIn(
            "Abcdef12!xyz",
            email.body,
        )

        self.assertIn(
            "alice@example.com",
            email.body,
        )

    def test_resend_invalidates_previous_password(self):
        user = self.create_user()

        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="FirstPwd1!xy",
        ):
            TemporaryPasswordService.reset_and_send(
                user=user,
            )

        user.refresh_from_db()

        self.assertTrue(
            user.check_password(
                "FirstPwd1!xy"
            )
        )

        with patch.object(
            TemporaryPasswordService,
            "generate_password",
            return_value="SecondPwd2!x",
        ):
            TemporaryPasswordService.reset_and_send(
                user=user,
            )

        user.refresh_from_db()

        self.assertFalse(
            user.check_password(
                "FirstPwd1!xy"
            )
        )

        self.assertTrue(
            user.check_password(
                "SecondPwd2!x"
            )
        )

    def test_reset_and_send_rejects_inactive_user(self):
        user = self.create_user()
        user.is_active = False
        user.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        with self.assertRaises(ValueError):
            TemporaryPasswordService.reset_and_send(
                user=user,
            )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_reset_and_send_rolls_back_when_email_fails(self):
        user = self.create_user()

        old_password = user.password

        with patch(
            (
                "apps.users.services."
                "temporary_password_service."
                "EmailMessage.send"
            ),
            side_effect=RuntimeError(
                "SMTP indisponible"
            ),
        ):
            with self.assertRaises(RuntimeError):
                TemporaryPasswordService.reset_and_send(
                    user=user,
                )

        user.refresh_from_db()

        self.assertEqual(
            user.password,
            old_password,
        )

        self.assertFalse(
            user.must_change_password
        )

        self.assertIsNone(
            user.temporary_password_sent_at
        )
        
class UserAuthenticationTests(
    UserTestDataMixin,
    TestCase,
):
    TEMPORARY_PASSWORD = "TempPwd1!"
    PERSONAL_PASSWORD = "Z7!qP2#m"

    def create_auth_user(
        self,
        *,
        email: str = "auth.user@example.com",
        must_change_password: bool = False,
        password: str | None = None,
    ):
        user = self.create_user(
            email=email,
        )

        user.set_password(
            password
            or self.PERSONAL_PASSWORD
        )

        user.must_change_password = (
            must_change_password
        )

        user.save(
            update_fields=[
                "password",
                "must_change_password",
                "updated_at",
            ]
        )

        return user

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def test_login_with_valid_credentials(self):
        user = self.create_auth_user()

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": user.email,
                "password": self.PERSONAL_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )

        self.assertEqual(
            str(
                self.client.session[
                    "_auth_user_id"
                ]
            ),
            str(user.pk),
        )

    def test_login_rejects_invalid_password(self):
        user = self.create_auth_user()

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": user.email,
                "password": "WrongPassword!",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    # ------------------------------------------------------------------
    # Mot de passe provisoire
    # ------------------------------------------------------------------

    def test_temporary_password_redirects_to_required_change(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": user.email,
                "password": self.TEMPORARY_PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "users:password-change-required"
            ),
        )

    def test_required_password_change_cannot_be_bypassed(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        self.client.force_login(
            user
        )

        response = self.client.get(
            "/projects/"
        )

        self.assertRedirects(
            response,
            reverse(
                "users:password-change-required"
            ),
            fetch_redirect_response=False,
        )

    # ------------------------------------------------------------------
    # Nouveau mot de passe
    # ------------------------------------------------------------------

    def test_required_password_change_updates_password(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        self.client.force_login(
            user
        )

        response = self.client.post(
            reverse(
                "users:password-change-required"
            ),
            data={
                "new_password": (
                    self.PERSONAL_PASSWORD
                ),
                "new_password_confirmation": (
                    self.PERSONAL_PASSWORD
                ),
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )

        user.refresh_from_db()

        self.assertFalse(
            user.must_change_password
        )

        self.assertFalse(
            user.check_password(
                self.TEMPORARY_PASSWORD
            )
        )

        self.assertTrue(
            user.check_password(
                self.PERSONAL_PASSWORD
            )
        )

    def test_required_password_change_rejects_short_password(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        self.client.force_login(
            user
        )

        response = self.client.post(
            reverse(
                "users:password-change-required"
            ),
            data={
                "new_password": "Ab1!xyz",
                "new_password_confirmation": "Ab1!xyz",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "new_password",
            response.context["form"].errors,
        )

        user.refresh_from_db()

        self.assertTrue(
            user.must_change_password
        )

    def test_session_is_preserved_after_password_change(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        self.client.force_login(
            user
        )

        self.client.post(
            reverse(
                "users:password-change-required"
            ),
            data={
                "new_password": (
                    self.PERSONAL_PASSWORD
                ),
                "new_password_confirmation": (
                    self.PERSONAL_PASSWORD
                ),
            },
        )

        response = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            str(
                self.client.session[
                    "_auth_user_id"
                ]
            ),
            str(user.pk),
        )

    # ------------------------------------------------------------------
    # Logout / reconnexion
    # ------------------------------------------------------------------

    def test_logout_ends_authenticated_session(
        self,
    ):
        user = self.create_auth_user()

        self.client.force_login(
            user
        )

        response = self.client.post(
            reverse("users:logout")
        )

        self.assertRedirects(
            response,
            reverse("users:login"),
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_user_can_login_again_with_personal_password(
        self,
    ):
        user = self.create_auth_user(
            must_change_password=True,
            password=self.TEMPORARY_PASSWORD,
        )

        self.client.force_login(
            user
        )

        self.client.post(
            reverse(
                "users:password-change-required"
            ),
            data={
                "new_password": (
                    self.PERSONAL_PASSWORD
                ),
                "new_password_confirmation": (
                    self.PERSONAL_PASSWORD
                ),
            },
        )

        self.client.post(
            reverse("users:logout")
        )

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": user.email,
                "password": (
                    self.PERSONAL_PASSWORD
                ),
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )