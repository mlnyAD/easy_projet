

from django.test import TestCase

from apps.companies.models import Company
from apps.users.models import User
from apps.users.services.list_preference import (
    UserListPreferenceService,
)
from framework.dictionary import EntityDefinition
from framework.list import ColumnDefinition, ListDefinition


class UserListPreferenceServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société tests préférences listes",
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="preferences-listes@example.com",
            first_name="Jeanne",
            last_name="Préférence",
        )

    def setUp(self):
        self.definition = self._build_definition()

    @staticmethod
    def _build_definition() -> ListDefinition:
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
            identifier="test_company_list",
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

    def test_returns_definition_default_when_no_preference_exists(self):
        identifiers = (
            UserListPreferenceService
            .get_visible_column_identifiers(
                user=self.user,
                definition=self.definition,
            )
        )

        self.assertEqual(
            identifiers,
            (
                "name",
                "email",
                "city",
            ),
        )

    def test_saves_selected_columns_in_definition_order(self):
        UserListPreferenceService.save_visible_column_identifiers(
            user=self.user,
            definition=self.definition,
            identifiers=(
                "city",
                "name",
            ),
        )

        identifiers = (
            UserListPreferenceService
            .get_visible_column_identifiers(
                user=self.user,
                definition=self.definition,
            )
        )

        self.assertEqual(
            identifiers,
            (
                "name",
                "city",
            ),
        )

    def test_rejects_empty_selection(self):
        with self.assertRaisesRegex(
            ValueError,
            "Au moins une colonne",
        ):
            UserListPreferenceService.save_visible_column_identifiers(
                user=self.user,
                definition=self.definition,
                identifiers=(),
            )

    def test_rejects_unknown_column(self):
        with self.assertRaisesRegex(
            ValueError,
            "n'existe pas",
        ):
            UserListPreferenceService.save_visible_column_identifiers(
                user=self.user,
                definition=self.definition,
                identifiers=(
                    "unknown",
                ),
            )