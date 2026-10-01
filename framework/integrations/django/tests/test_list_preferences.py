

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.views import View

from apps.companies.models import Company
from apps.users.models import User
from framework.dictionary import EntityDefinition
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.list import ColumnDefinition, ListDefinition


def build_test_list_definition() -> ListDefinition:
    entity = EntityDefinition(
        {
            "entity": {
                "name": "test_company",
                "label": "Société",
                "label_plural": "Sociétés",
            },
            "fields": {
                "name": {
                    "label": "Nom",
                    "data_type": "string",
                    "required": True,
                    "max_length": 255,
                },
                "email": {
                    "label": "Adresse électronique",
                    "data_type": "email",
                    "required": False,
                    "max_length": 255,
                },
                "city": {
                    "label": "Ville",
                    "data_type": "string",
                    "required": False,
                    "max_length": 255,
                },
            },
        }
    )

    return ListDefinition(
        identifier="test_list_preferences",
        entity=entity,
        columns=(
            ColumnDefinition(
                field=entity.get_field("name"),
                order=10,
            ),
            ColumnDefinition(
                field=entity.get_field("email"),
                order=20,
            ),
            ColumnDefinition(
                field=entity.get_field("city"),
                order=30,
            ),
        ),
        default_sort="name",
    )


class TestListPreferenceView(
    EPListPreferencesMixin,
    View,
):
    list_definition = build_test_list_definition()


class EPListPreferencesMixinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test mixin préférences",
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="mixin-preferences@example.com",
            first_name="Paul",
            last_name="Liste",
        )

    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_user_gets_default_visible_columns(self):
        request = self.factory.get("/test-list/")
        request.user = AnonymousUser()

        view = TestListPreferenceView()
        view.request = request

        identifiers = view.get_visible_column_identifiers()

        self.assertEqual(
            identifiers,
            (
                "name",
                "email",
                "city",
            ),
        )

    def test_post_saves_user_visible_columns(self):
        request = self.factory.post(
            "/test-list/?page=2",
            data={
                "visible_columns": (
                    "city",
                    "name",
                ),
            },
        )
        request.user = self.user

        response = TestListPreferenceView.as_view()(request)

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response["Location"],
            "/test-list/?page=2",
        )

        get_request = self.factory.get("/test-list/")
        get_request.user = self.user

        view = TestListPreferenceView()
        view.request = get_request

        identifiers = view.get_visible_column_identifiers()

        self.assertEqual(
            identifiers,
            (
                "name",
                "city",
            ),
        )

    def test_post_rejects_empty_selection(self):
        request = self.factory.post(
            "/test-list/",
            data={},
        )
        request.user = self.user

        response = TestListPreferenceView.as_view()(request)

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_post_requires_authenticated_user(self):
        request = self.factory.post(
            "/test-list/",
            data={
                "visible_columns": (
                    "name",
                ),
            },
        )
        request.user = AnonymousUser()

        response = TestListPreferenceView.as_view()(request)

        self.assertEqual(
            response.status_code,
            403,
        )