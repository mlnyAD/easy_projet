

from django.test import TestCase
from django.urls import reverse

from apps.companies.models import Company
from common.constants import (
    DEFAULT_PAGE_SIZE,
    PAGE_SIZE_VALUES,
)

class CompanyListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="AXCIO DATA",
            siret="12345678900012",
            vat_number="FR12345678901",
            email="contact@axcio-data.fr",
            phone="0123456789",
            address_1="1 rue de Paris",
            postal_code="75001",
            city="PARIS",
            country="FRANCE",
            is_active=True,
        )

    def test_company_list_returns_http_200(self):
        response = self.client.get(reverse("companies:list"))

        self.assertEqual(response.status_code, 200)

    def test_company_list_uses_expected_template(self):
        response = self.client.get(reverse("companies:list"))

        self.assertTemplateUsed(
            response,
            "companies/company_list.html",
        )

    def test_company_list_contains_company(self):
        response = self.client.get(reverse("companies:list"))

        self.assertContains(response, "AXCIO DATA")
        self.assertContains(response, "contact@axcio-data.fr")
        self.assertContains(response, "PARIS")

    def test_company_list_contains_create_link(self):
        response = self.client.get(reverse("companies:list"))

        self.assertContains(
            response,
            reverse("companies:create"),
        )

    def test_company_list_contains_update_link(self):
        response = self.client.get(reverse("companies:list"))

        self.assertContains(
            response,
            reverse(
                "companies:update",
                kwargs={"pk": self.company.pk},
            ),
        )

    def test_company_list_exposes_framework_view_model(self):
        response = self.client.get(reverse("companies:list"))

        self.assertIn("list", response.context)
        self.assertIn("page_sizes", response.context)
        self.assertEqual(
            response.context["page_sizes"],
            PAGE_SIZE_VALUES,
        )

    def test_company_list_uses_default_page_size(self):
        for index in range(DEFAULT_PAGE_SIZE):
            Company.objects.create(
                name=f"SOCIETE {index:02d}",
                email=f"company{index}@example.com",
                city="PARIS",
                country="FRANCE",
                is_active=True,
            )

        response = self.client.get(reverse("companies:list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            len(response.context["page_obj"].object_list),
            DEFAULT_PAGE_SIZE,
        )
            
class CompanyCreateViewTests(TestCase):
    def test_create_page_returns_http_200(self):
        response = self.client.get(reverse("companies:create"))

        self.assertEqual(response.status_code, 200)

    def test_create_page_uses_template(self):
        response = self.client.get(reverse("companies:create"))

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )
    
    def test_create_page_contains_form(self):
        response = self.client.get(reverse("companies:create"))

        self.assertIn("form", response.context)

    def test_create_company(self):
        response = self.client.post(
            reverse("companies:create"),
            data={
                "name": "SOCIETE TEST",
                "siret": "12345678900012",
                "vat_number": "FR12345678901",
                "email": "contact@test.fr",
                "phone": "0123456789",
                "address_1": "1 rue de Paris",
                "address_2": "",
                "address_3": "",
                "postal_code": "75001",
                "city": "PARIS",
                "country": "FRANCE",
                "is_active": True,
            },
        )

        self.assertRedirects(
            response,
            reverse("companies:list"),
        )

        self.assertTrue(
            Company.objects.filter(
                name="SOCIETE TEST",
            ).exists()
        )        