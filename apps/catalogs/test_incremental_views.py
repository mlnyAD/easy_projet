

from __future__ import annotations

import json

from django.test import TestCase
from django.urls import reverse

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)


class IncrementalCatalogViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.incremental_catalog = (
            CatalogType.objects.create(
                code="TEST_INCREMENTAL",
                label="Catalogue incrémental",
                is_active=True,
                is_editable=True,
                is_incremental=True,
            )
        )

        cls.readonly_catalog = (
            CatalogType.objects.create(
                code="TEST_READONLY",
                label="Catalogue non modifiable",
                is_active=True,
                is_editable=False,
                is_incremental=False,
            )
        )

        cls.non_incremental_catalog = (
            CatalogType.objects.create(
                code="TEST_NON_INCREMENTAL",
                label="Catalogue modifiable",
                is_active=True,
                is_editable=True,
                is_incremental=False,
            )
        )

        cls.inactive_catalog = (
            CatalogType.objects.create(
                code="TEST_INACTIVE",
                label="Catalogue inactif",
                is_active=False,
                is_editable=True,
                is_incremental=True,
            )
        )

        cls.url = reverse(
            "catalogs:incremental-create"
        )

    def post_json(
        self,
        *,
        catalog_code: str,
        label: str,
    ):
        return self.client.post(
            self.url,
            data=json.dumps(
                {
                    "catalog_code": catalog_code,
                    "label": label,
                }
            ),
            content_type="application/json",
        )

    def test_create_incremental_value(self):
        response = self.post_json(
            catalog_code="TEST_INCREMENTAL",
            label="Nouvelle valeur",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["value"]["code"],
            "NOUVELLE_VALEUR",
        )
        self.assertEqual(
            payload["value"]["label"],
            "Nouvelle valeur",
        )

        value = CatalogValue.objects.get(
            catalog_type=self.incremental_catalog,
            code="NOUVELLE_VALEUR",
        )

        self.assertEqual(
            value.label,
            "Nouvelle valeur",
        )
        self.assertFalse(value.is_system)
        self.assertTrue(value.is_active)

    def test_label_is_trimmed(self):
        response = self.post_json(
            catalog_code="TEST_INCREMENTAL",
            label="  Peintre  ",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        value = CatalogValue.objects.get(
            catalog_type=self.incremental_catalog,
            code="PEINTRE",
        )

        self.assertEqual(value.label, "Peintre")

    def test_empty_label_is_rejected(self):
        response = self.post_json(
            catalog_code="TEST_INCREMENTAL",
            label="   ",
        )

        self.assertEqual(
            response.status_code,
            400,
        )
        self.assertFalse(
            response.json()["success"]
        )

    def test_unknown_catalog_is_rejected(self):
        response = self.post_json(
            catalog_code="UNKNOWN",
            label="Valeur",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_inactive_catalog_is_rejected(self):
        response = self.post_json(
            catalog_code="TEST_INACTIVE",
            label="Valeur",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_readonly_catalog_is_rejected(self):
        response = self.post_json(
            catalog_code="TEST_READONLY",
            label="Valeur",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_non_incremental_catalog_is_rejected(self):
        response = self.post_json(
            catalog_code="TEST_NON_INCREMENTAL",
            label="Valeur",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_duplicate_value_is_rejected(self):
        CatalogValue.objects.create(
            catalog_type=self.incremental_catalog,
            code="PEINTRE",
            label="Peintre",
            is_active=True,
        )

        response = self.post_json(
            catalog_code="TEST_INCREMENTAL",
            label="Peintre",
        )

        self.assertEqual(
            response.status_code,
            409,
        )

        self.assertEqual(
            CatalogValue.objects.filter(
                catalog_type=self.incremental_catalog,
                code="PEINTRE",
            ).count(),
            1,
        )

    def test_invalid_json_is_rejected(self):
        response = self.client.post(
            self.url,
            data="{invalid",
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_get_method_is_rejected(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            405,
        )