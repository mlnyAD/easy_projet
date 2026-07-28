

import uuid

from django.core.validators import RegexValidator
from django.db import models

from common.models import TimeStampedModel


siret_validator = RegexValidator(
    regex=r"^\d{14}$",
    message="Le SIRET doit contenir exactement 14 chiffres.",
)


class Company(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nom usuel",
    )

    siret = models.CharField(
        "SIRET",
        max_length=14,
        blank=True,
        validators=[siret_validator],
    )

    vat_number = models.CharField(
        "Numéro de TVA intracommunautaire",
        max_length=32,
        blank=True,
    )

    email = models.EmailField(
        max_length=254,
        blank=True,
        verbose_name="Adresse électronique",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
    )

    address_1 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Adresse",
    )

    address_2 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Complément d'adresse",
    )

    address_3 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Complément d'adresse 2",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code postal",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville",
    )

    country = models.CharField(
        max_length=100,
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