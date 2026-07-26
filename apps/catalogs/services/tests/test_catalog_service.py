

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.catalogs.services import CatalogService


class CatalogServiceGetChoicesTests(TestCase):
    """Tests de CatalogService.get_choices()."""

    def setUp(self) -> None:
        self.catalog_type = CatalogType.objects.create(
            code="TEST_STATUS",
            label="Statut de test",
            is_active=True,
        )

        self.first_value = CatalogValue.objects.create(
            catalog_type=self.catalog_type,
            code="FIRST",
            label="Première valeur",
            level=0,
            sort_order=10,
            is_active=True,
        )

        self.second_value = CatalogValue.objects.create(
            catalog_type=self.catalog_type,
            code="SECOND",
            label="Deuxième valeur",
            level=0,
            sort_order=20,
            is_active=True,
        )

    def test_get_choices_returns_active_catalog_values(self) -> None:
        choices = CatalogService.get_choices("TEST_STATUS")

        self.assertEqual(
            choices,
            [
                (str(self.first_value.pk), "Première valeur"),
                (str(self.second_value.pk), "Deuxième valeur"),
            ],
        )

    def test_get_choices_normalizes_catalog_code(self) -> None:
        expected = CatalogService.get_choices("TEST_STATUS")

        result = CatalogService.get_choices(" test_status ")

        self.assertEqual(result, expected)

    def test_get_choices_returns_empty_list_for_unknown_catalog(self) -> None:
        choices = CatalogService.get_choices("UNKNOWN_CATALOG")

        self.assertEqual(choices, [])

    def test_get_choices_excludes_inactive_values(self) -> None:
        inactive_value = CatalogValue.objects.create(
            catalog_type=self.catalog_type,
            code="INACTIVE",
            label="Valeur inactive",
            level=0,
            sort_order=5,
            is_active=False,
        )

        choices = CatalogService.get_choices("TEST_STATUS")
        returned_ids = [choice_id for choice_id, _label in choices]

        self.assertNotIn(str(inactive_value.pk), returned_ids)

    def test_get_choices_returns_empty_list_for_inactive_catalog(self) -> None:
        self.catalog_type.is_active = False
        self.catalog_type.save(update_fields=["is_active", "updated_at"])

        choices = CatalogService.get_choices("TEST_STATUS")

        self.assertEqual(choices, [])

    def test_get_choices_orders_by_level_sort_order_and_label(self) -> None:
        ordered_catalog = CatalogType.objects.create(
            code="ORDER_TEST",
            label="Test de tri",
            is_hierarchical=True,
            is_active=True,
        )

        parent = CatalogValue.objects.create(
            catalog_type=ordered_catalog,
            code="PARENT",
            label="Parent",
            level=0,
            sort_order=50,
            is_active=True,
        )

        alphabetical_second = CatalogValue.objects.create(
            catalog_type=ordered_catalog,
            code="ALPHABETICAL_SECOND",
            label="Bêta",
            level=0,
            sort_order=10,
            is_active=True,
        )

        alphabetical_first = CatalogValue.objects.create(
            catalog_type=ordered_catalog,
            code="ALPHABETICAL_FIRST",
            label="Alpha",
            level=0,
            sort_order=10,
            is_active=True,
        )

        child = CatalogValue.objects.create(
            catalog_type=ordered_catalog,
            code="CHILD",
            label="Enfant",
            parent=parent,
            level=1,
            sort_order=0,
            is_active=True,
        )

        choices = CatalogService.get_choices("ORDER_TEST")

        self.assertEqual(
            choices,
            [
                (str(alphabetical_first.pk), "Alpha"),
                (str(alphabetical_second.pk), "Bêta"),
                (str(parent.pk), "Parent"),
                (str(child.pk), "Enfant"),
            ],
        )