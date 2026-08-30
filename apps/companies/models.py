

import uuid

from django.core.validators import RegexValidator
from django.db import models

from common.constants.company import (
    COMPANY_ADDRESS_LENGTH,
    COMPANY_CITY_LENGTH,
    COMPANY_COUNTRY_LENGTH,
    COMPANY_EMAIL_LENGTH,
    COMPANY_NAME_LENGTH,
    COMPANY_PHONE_LENGTH,
    COMPANY_POSTAL_CODE_LENGTH,
    COMPANY_SIRET_LENGTH,
    COMPANY_VAT_NUMBER_LENGTH,
)
from common.models import TimeStampedModel


siret_validator = RegexValidator(
    regex=rf"^\d{{{COMPANY_SIRET_LENGTH}}}$",
    message=(
        f"Le SIRET doit contenir exactement "
        f"{COMPANY_SIRET_LENGTH} chiffres."
    ),
)


class Company(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    name = models.CharField(
        max_length=COMPANY_NAME_LENGTH,
        verbose_name="Nom usuel",
    )

    logo = models.ImageField(
        upload_to="companies/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
    )

    siret = models.CharField(
        "SIRET",
        max_length=COMPANY_SIRET_LENGTH,
        blank=True,
        validators=[siret_validator],
    )

    vat_number = models.CharField(
        "Numéro de TVA intracommunautaire",
        max_length=COMPANY_VAT_NUMBER_LENGTH,
        blank=True,
    )

    email = models.EmailField(
        max_length=COMPANY_EMAIL_LENGTH,
        blank=True,
        verbose_name="Adresse électronique",
    )

    phone = models.CharField(
        max_length=COMPANY_PHONE_LENGTH,
        blank=True,
        verbose_name="Téléphone",
    )

    address_1 = models.CharField(
        max_length=COMPANY_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Adresse",
    )

    address_2 = models.CharField(
        max_length=COMPANY_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Complément d'adresse",
    )

    address_3 = models.CharField(
        max_length=COMPANY_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Complément d'adresse 2",
    )

    postal_code = models.CharField(
        max_length=COMPANY_POSTAL_CODE_LENGTH,
        blank=True,
        verbose_name="Code postal",
    )

    city = models.CharField(
        max_length=COMPANY_CITY_LENGTH,
        blank=True,
        verbose_name="Ville",
    )

    country = models.CharField(
        max_length=COMPANY_COUNTRY_LENGTH,
        blank=True,
        verbose_name="Pays",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    def save(self, *args, **kwargs):
        self.siret = "".join((self.siret or "").split())
        self.vat_number = (self.vat_number or "").strip().upper()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "company"
        ordering = ["name"]
        verbose_name = "Société"
        verbose_name_plural = "Sociétés"

    def __str__(self):
        return self.name