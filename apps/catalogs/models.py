

from django.core.exceptions import ValidationError
from django.db import models

from common.constants.catalog import (
    CATALOG_CODE_LENGTH,
    CATALOG_LABEL_LENGTH,
)
from common.models import TimeStampedModel


class CatalogType(TimeStampedModel):
    code = models.CharField(
        max_length=CATALOG_CODE_LENGTH,
        unique=True,
        verbose_name="Code",
    )
    label = models.CharField(
        max_length=CATALOG_LABEL_LENGTH,
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
        super().clean()

        if self.is_incremental and not self.is_editable:
            raise ValidationError(
                {
                    "is_incremental": (
                        "Un catalogue incrémental doit être modifiable."
                    )
                }
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
        max_length=CATALOG_CODE_LENGTH,
        verbose_name="Code",
    )
    label = models.CharField(
        max_length=CATALOG_LABEL_LENGTH,
        verbose_name="Libellé",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Valeur parente",
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
        ordering = [
            "catalog_type",
            "level",
            "sort_order",
            "label",
        ]
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

    def clean(self):
        super().clean()

        if self.parent is not None:
            if self.parent.catalog_type_id != self.catalog_type_id:
                raise ValidationError(
                    {
                        "parent": (
                            "La valeur parente doit appartenir "
                            "au même catalogue."
                        )
                    }
                )

            if not self.catalog_type.is_hierarchical:
                raise ValidationError(
                    {
                        "parent": (
                            "Un catalogue non hiérarchique "
                            "ne peut pas avoir de valeur parente."
                        )
                    }
                )

            expected_level = self.parent.level + 1

            if self.level != expected_level:
                raise ValidationError(
                    {
                        "level": (
                            f"Le niveau attendu est {expected_level} "
                            "pour cette valeur parente."
                        )
                    }
                )

        elif not self.catalog_type.is_hierarchical and self.level != 0:
            raise ValidationError(
                {
                    "level": (
                        "Le niveau d'une valeur appartenant à un "
                        "catalogue non hiérarchique doit être égal à 0."
                    )
                }
            )

        if self.is_default and not self.is_active:
            raise ValidationError(
                {
                    "is_default": (
                        "Une valeur inactive ne peut pas être "
                        "la valeur par défaut."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.catalog_type.code} - {self.label}"