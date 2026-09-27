

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import ClientEnvironment
from common.models import TimeStampedModel


class DocumentFolderTemplate(TimeStampedModel):
    """
    Arborescence documentaire réutilisable pour un environnement client.

    Une seule arborescence active peut être définie par défaut
    dans un même environnement. Elle est appliquée à la création
    de chaque nouveau projet de cet environnement.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    client_environment = models.ForeignKey(
        ClientEnvironment,
        on_delete=models.PROTECT,
        related_name="document_folder_templates",
        verbose_name="Environnement client",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nom",
    )

    description = models.TextField(
        blank=True,
        max_length=2000,
        verbose_name="Description",
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="Arborescence par défaut",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    class Meta:
        db_table = "document_folder_template"
        ordering = [
            "client_environment__company__name",
            "name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                    "name",
                ],
                name="uq_doc_folder_tpl_env_name",
            ),
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                ],
                condition=Q(
                    is_default=True,
                    is_active=True,
                ),
                name="uq_doc_folder_tpl_env_default",
            ),
        ]
        verbose_name = "Modèle d'arborescence documentaire"
        verbose_name_plural = (
            "Modèles d'arborescences documentaires"
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.is_default
            and not self.is_active
        ):
            errors["is_default"] = (
                "Une arborescence par défaut doit être active."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.description = self.description.strip()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.client_environment} - "
            f"{self.name}"
        )


class DocumentFolderTemplateFolder(TimeStampedModel):
    """
    Dossier appartenant à un modèle d'arborescence documentaire.

    La structure est indépendante des projets. Elle est copiée
    dans les dossiers DocumentFolder lors de la création du projet.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    template = models.ForeignKey(
        DocumentFolderTemplate,
        on_delete=models.CASCADE,
        related_name="folders",
        verbose_name="Modèle d'arborescence",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        verbose_name="Dossier parent",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nom",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    class Meta:
        db_table = "document_folder_template_folder"
        ordering = [
            "template",
            "parent__sort_order",
            "parent__name",
            "sort_order",
            "name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "template",
                    "name",
                ],
                condition=Q(
                    parent__isnull=True,
                ),
                name="uq_doc_folder_tpl_root_name",
            ),
            models.UniqueConstraint(
                fields=[
                    "template",
                    "parent",
                    "name",
                ],
                condition=Q(
                    parent__isnull=False,
                ),
                name="uq_doc_folder_tpl_child_name",
            ),
        ]
        verbose_name = "Dossier de modèle d'arborescence"
        verbose_name_plural = (
            "Dossiers de modèles d'arborescences"
        )

    def clean(self):
        super().clean()

        if (
            self.parent_id
            and self.parent.template_id != self.template_id
        ):
            raise ValidationError(
                {
                    "parent": (
                        "Le dossier parent doit appartenir "
                        "au même modèle d'arborescence."
                    ),
                }
            )

        if (
            self.parent_id
            and self.pk
            and self.parent_id == self.pk
        ):
            raise ValidationError(
                {
                    "parent": (
                        "Un dossier ne peut pas être son "
                        "propre parent."
                    ),
                }
            )

        ancestor = self.parent

        while ancestor is not None:
            if (
                self.pk
                and ancestor.pk == self.pk
            ):
                raise ValidationError(
                    {
                        "parent": (
                            "Un dossier ne peut pas être déplacé "
                            "dans l'un de ses descendants."
                        ),
                    }
                )

            ancestor = ancestor.parent

    def save(self, *args, **kwargs):
        self.name = self.name.strip()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.template} - "
            f"{self.name}"
        )