

import uuid

from django.db import models

from common.models import TimeStampedModel


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

    email = models.EmailField(
        max_length=254,
        verbose_name="Adresse électronique",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
    )

    address_1 = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Adresse",
    )

    address_2 = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Complément d'adresse",
    )

    address_3 = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Complément d'adresse 2",
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code postal",
    )

    city = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Ville",
    )

    country = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Pays",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    class Meta:
        db_table = "company"
        ordering = ["name"]
        verbose_name = "Société"
        verbose_name_plural = "Sociétés"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name