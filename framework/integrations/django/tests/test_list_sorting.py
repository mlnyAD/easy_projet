

from django.test import RequestFactory, TestCase
from django.views.generic import ListView

from apps.companies.models import Company
from framework.dictionary import EntityDefinition
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.list import ColumnDefinition, ListDefinition


def build_test_list_definition() -> ListDefinition:
    entity = EntityDefinition(
        {
            "entity": {
                "name": "company",
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
            },
        }
    )

    return ListDefinition(
        identifier="test_list_sorting",
        entity=entity,
        columns=(
            ColumnDefinition(
                field=entity.get_field("name"),
                order=10,
            ),
            ColumnDefinition(
                field=entity.get_field("email"),
                sortable=False,
                order=20,
            ),
        ),
        default_sort="name",
    )


class TestListSortingView(
    EPListSortingMixin,
    ListView,
):
    model = Company
    list_definition = build_test_list_definition()


class EPListSortingMixinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Company.objects.create(
            name="BETA",
        )

        Company.objects.create(
            name="ALPHA",
        )

        Company.objects.create(
            name="GAMMA",
        )

    def setUp(self):
        self.factory = RequestFactory()

    def test_uses_default_sort_when_no_parameter_is_provided(
        self,
    ):
        request = self.factory.get("/test-list/")

        view = TestListSortingView()
        view.request = request

        names = list(
            view.get_queryset().values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            names,
            [
                "ALPHA",
                "BETA",
                "GAMMA",
            ],
        )

    def test_applies_descending_sort_from_url_parameters(self):
        request = self.factory.get(
            "/test-list/",
            {
                "sort": "name",
                "direction": "desc",
            },
        )

        view = TestListSortingView()
        view.request = request

        names = list(
            view.get_queryset().values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            names,
            [
                "GAMMA",
                "BETA",
                "ALPHA",
            ],
        )

    def test_falls_back_to_default_sort_for_unknown_column(self):
        request = self.factory.get(
            "/test-list/",
            {
                "sort": "unknown",
                "direction": "desc",
            },
        )

        view = TestListSortingView()
        view.request = request

        self.assertEqual(
            view.get_sort_by(),
            "name",
        )

    def test_falls_back_to_default_sort_for_non_sortable_column(
        self,
    ):
        request = self.factory.get(
            "/test-list/",
            {
                "sort": "email",
            },
        )

        view = TestListSortingView()
        view.request = request

        self.assertEqual(
            view.get_sort_by(),
            "name",
        )