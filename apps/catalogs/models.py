

from django.core.exceptions import ValidationError
from django.db import models

from common.constants import CODE_LENGTH, LABEL_LENGTH
from common.models import TimeStampedModel


class CatalogType(TimeStampedModel):
    code = models.CharField(
        max_length=CODE_LENGTH,
        unique=True,
        verbose_name="Code",
    )
    label = models.CharField(
        max_length=LABEL_LENGTH,
        verbose_name="Libellé",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    is_hierarchical = models.BooleanField(
        default=False,
        verbose_name="Hiérarchique",
    )
    is_editable = models.BooleanField(
        default=False,
        verbose_name="Modifiable",
    )
    is_incremental = models.BooleanField(
        default=False,
        verbose_name="Incrémental",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    class Meta:
        db_table = "catalog_type"
        ordering = ["label"]
        verbose_name = "Type de catalogue"
        verbose_name_plural = "Types de catalogues"

    def clean(self):
        if self.is_incremental and not self.is_editable:
            raise ValidationError(
                "Un catalogue incrémental doit être modifiable."
            )

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


class CatalogValue(TimeStampedModel):
    catalog_type = models.ForeignKey(
        CatalogType,
        on_delete=models.PROTECT,
        related_name="values",
        verbose_name="Type de catalogue",
    )

    code = models.CharField(
        max_length=CODE_LENGTH,
        verbose_name="Code",
    )
    label = models.CharField(
        max_length=LABEL_LENGTH,
        verbose_name="Libellé",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    level = models.PositiveIntegerField(
        default=0,
        verbose_name="Niveau",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Système",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Valeur par défaut",
    )

    class Meta:
        db_table = "catalog_value"
        ordering = ["catalog_type", "sort_order", "label"]
        verbose_name = "Valeur de catalogue"
        verbose_name_plural = "Valeurs de catalogue"
        constraints = [
            models.UniqueConstraint(
                fields=["catalog_type", "code"],
                name="uniq_catalog_value_type_code",
            ),
            models.UniqueConstraint(
                fields=["catalog_type"],
                condition=models.Q(is_default=True),
                name="uniq_default_value_by_catalog_type",
            ),
        ]

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.catalog_type.code} - {self.label}"