

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import ClientEnvironment
from django.core.exceptions import ValidationError

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from apps.users.models import User
from common.constants.project import (
    PROJECT_ADDRESS_LENGTH,
    PROJECT_AMOUNT_DECIMAL_PLACES,
    PROJECT_AMOUNT_MAX_DIGITS,
    PROJECT_CITY_LENGTH,
    PROJECT_COMMENT_LENGTH,
    PROJECT_CONTRACT_REFERENCE_LENGTH,
    PROJECT_COUNTRY_LENGTH,
    PROJECT_CURRENCY_LENGTH,
    PROJECT_DEFAULT_AMOUNT,
    PROJECT_DEFAULT_CURRENCY,
    PROJECT_DEFAULT_WORKLOAD_HOURS,
    PROJECT_DESCRIPTION_LENGTH,
    PROJECT_NAME_LENGTH,
    PROJECT_POSTAL_CODE_LENGTH,
    PROJECT_REFERENCE_LENGTH,
    PROJECT_COORDINATE_MAX_DIGITS,
    PROJECT_COORDINATE_DECIMAL_PLACES,
)
from common.models import TimeStampedModel


class Project(TimeStampedModel):
    """
    Projet contractuel et opérationnel géré dans Easy Projet.

    Le projet décrit ce qui a été vendu et accepté par le client.
    Les coûts internes, prix de revient et marges relèvent du module
    financier et ne sont pas stockés dans ce modèle.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    reference = models.CharField(
        max_length=PROJECT_REFERENCE_LENGTH,
        unique=True,
        verbose_name="Référence",
    )

    name = models.CharField(
        max_length=PROJECT_NAME_LENGTH,
        verbose_name="Nom du projet",
    )

    description = models.TextField(
        max_length=PROJECT_DESCRIPTION_LENGTH,
        blank=True,
        verbose_name="Description",
    )

    client_environment = models.ForeignKey(
        ClientEnvironment,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="Environnement client",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="managed_projects",
        verbose_name="Société responsable",
    )

    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="managed_projects",
        null=True,
        blank=True,
        verbose_name="Chef de projet",
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="status_projects",
        verbose_name="Statut",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Projet actif",
    )

    # ------------------------------------------------------------------
    # Client et contrat
    # ------------------------------------------------------------------

    owner_company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="owned_projects",
        null=True,
        blank=True,
        verbose_name="Maître d'ouvrage",
    )

    designer_company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="designed_projects",
        null=True,
        blank=True,
        verbose_name="Maître d'œuvre",
    )

    project_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="type_projects",
        null=True,
        blank=True,
        verbose_name="Type de projet",
    )

    contract_reference = models.CharField(
        max_length=PROJECT_CONTRACT_REFERENCE_LENGTH,
        blank=True,
        verbose_name="Référence contractuelle",
    )

    comments = models.TextField(
        max_length=PROJECT_COMMENT_LENGTH,
        blank=True,
        verbose_name="Commentaires",
    )

    # ------------------------------------------------------------------
    # Localisation
    # ------------------------------------------------------------------

    address_1 = models.CharField(
        max_length=PROJECT_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Adresse",
    )

    address_2 = models.CharField(
        max_length=PROJECT_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Complément d'adresse",
    )

    address_3 = models.CharField(
        max_length=PROJECT_ADDRESS_LENGTH,
        blank=True,
        verbose_name="Complément d'adresse 2",
    )

    postal_code = models.CharField(
        max_length=PROJECT_POSTAL_CODE_LENGTH,
        blank=True,
        verbose_name="Code postal",
    )

    city = models.CharField(
        max_length=PROJECT_CITY_LENGTH,
        blank=True,
        verbose_name="Ville",
    )

    country = models.CharField(
        max_length=PROJECT_COUNTRY_LENGTH,
        blank=True,
        verbose_name="Pays",
    )

    latitude = models.DecimalField(
        max_digits=PROJECT_COORDINATE_MAX_DIGITS,
        decimal_places=PROJECT_COORDINATE_DECIMAL_PLACES,
        null=True,
        blank=True,
        editable=False,
        verbose_name= "Latitude",
    )

    longitude = models.DecimalField(
        max_digits=PROJECT_COORDINATE_MAX_DIGITS,
        decimal_places=PROJECT_COORDINATE_DECIMAL_PLACES,
        null=True,
        blank=True,
        editable=False,
        verbose_name= "Longitude",
    )    

    # ------------------------------------------------------------------
    # Charge et planning
    # ------------------------------------------------------------------

    planned_workload_hours = models.PositiveIntegerField(
        default=PROJECT_DEFAULT_WORKLOAD_HOURS,
        verbose_name="Charge prévisionnelle (h)",
    )

    contractual_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date contractuelle de début",
    )

    contractual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date contractuelle de fin",
    )

    start_date_review = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date révisée de début",
    )

    end_date_review = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date révisée de fin",
    )

    receipt_date_init = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date initiale de réception",
    )

    receipt_date_review = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date révisée de réception",
    )

    delivery_date_init = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date initiale de livraison",
    )

    delivery_date_review = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date révisée de livraison",
    )

    # ------------------------------------------------------------------
    # Données commerciales partageables
    # ------------------------------------------------------------------

    amount_quote_ht = models.DecimalField(
        max_digits=PROJECT_AMOUNT_MAX_DIGITS,
        decimal_places=PROJECT_AMOUNT_DECIMAL_PLACES,
        default=PROJECT_DEFAULT_AMOUNT,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        verbose_name="Montant du devis HT",
    )

    amount_quote_ttc = models.DecimalField(
        max_digits=PROJECT_AMOUNT_MAX_DIGITS,
        decimal_places=PROJECT_AMOUNT_DECIMAL_PLACES,
        default=PROJECT_DEFAULT_AMOUNT,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        verbose_name="Montant du devis TTC",
    )

    amount_order_ht = models.DecimalField(
        max_digits=PROJECT_AMOUNT_MAX_DIGITS,
        decimal_places=PROJECT_AMOUNT_DECIMAL_PLACES,
        default=PROJECT_DEFAULT_AMOUNT,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        verbose_name="Montant de la commande HT",
    )

    amount_order_ttc = models.DecimalField(
        max_digits=PROJECT_AMOUNT_MAX_DIGITS,
        decimal_places=PROJECT_AMOUNT_DECIMAL_PLACES,
        default=PROJECT_DEFAULT_AMOUNT,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        verbose_name="Montant de la commande TTC",
    )

    currency = models.CharField(
        max_length=PROJECT_CURRENCY_LENGTH,
        default=PROJECT_DEFAULT_CURRENCY,
        verbose_name="Devise",
    )

    budget_comments = models.TextField(
        max_length=PROJECT_COMMENT_LENGTH,
        blank=True,
        verbose_name="Commentaires budgétaires",
    )

    def save(self, *args, **kwargs):
        """
        Normalise et sécurise le rattachement du projet.

        Si l'adresse d'un projet existant est modifiée,
        les coordonnées géographiques sont invalidées.
        Elles seront recalculées lors du prochain géocodage.
        """

        if self.company_id is None:
            raise ValueError(
                "La société responsable doit être renseignée."
            )

        try:
            environment = self.company.client_environment
        except ClientEnvironment.DoesNotExist as exc:
            raise ValueError(
                "La société responsable ne possède pas "
                "d'environnement client."
            ) from exc

        if (
            self.client_environment_id is not None
            and self.client_environment_id != environment.pk
        ):
            raise ValueError(
                "L'environnement client du projet ne correspond pas "
                "à sa société responsable."
            )

        self.client_environment = environment

        # --------------------------------------------------------------
        # Invalidation de la géolocalisation
        # --------------------------------------------------------------

        if self.pk:
            previous = (
                Project.objects
                .filter(pk=self.pk)
                .values(
                    "address_1",
                    "address_2",
                    "address_3",
                    "postal_code",
                    "city",
                    "country",
                )
                .first()
            )

            if previous is not None:
                address_changed = any(
                    (
                        previous[field_name] or ""
                    )
                    != (
                        getattr(self, field_name) or ""
                    )
                    for field_name in (
                        "address_1",
                        "address_2",
                        "address_3",
                        "postal_code",
                        "city",
                        "country",
                    )
                )

                if address_changed:
                    self.latitude = None
                    self.longitude = None

                    update_fields = kwargs.get("update_fields")

                    if update_fields is not None:
                        update_fields = set(update_fields)
                        update_fields.update(
                            {
                                "latitude",
                                "longitude",
                            }
                        )
                        kwargs["update_fields"] = update_fields

        # --------------------------------------------------------------
        # Normalisation
        # --------------------------------------------------------------

        self.reference = self.reference.strip().upper()
        self.name = self.name.strip()
        self.contract_reference = self.contract_reference.strip()

        self.currency = (
            self.currency.strip().upper()
            or PROJECT_DEFAULT_CURRENCY
        )

        super().save(*args, **kwargs)
                
    @property
    def effective_start_date(self):
        """
        Retourne la date de début actuellement retenue.

        La date révisée prévaut sur la date contractuelle.
        """
        return (
            self.start_date_review
            or self.contractual_start_date
        )

    @property
    def effective_end_date(self):
        """
        Retourne la date de fin actuellement retenue.

        La date révisée prévaut sur la date contractuelle.
        """
        return (
            self.end_date_review
            or self.contractual_end_date
        )

    @property
    def effective_receipt_date(self):
        """
        Retourne la date de réception actuellement retenue.

        La date révisée prévaut sur la date initiale.
        """
        return (
            self.receipt_date_review
            or self.receipt_date_init
        )

    @property
    def effective_delivery_date(self):
        """
        Retourne la date de livraison actuellement retenue.

        La date révisée prévaut sur la date initiale.
        """
        return (
            self.delivery_date_review
            or self.delivery_date_init
        )

    class Meta:
        db_table = "project"
        ordering = [
            "reference",
            "name",
        ]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self) -> str:
        return f"{self.reference} - {self.name}"
    
    
class ProjectMembership(TimeStampedModel):
    """
    Affectation d'un utilisateur à un projet.

    Une affectation active matérialise l'appartenance de
    l'utilisateur au projet. Le rôle doit appartenir au
    catalogue USER_PROJECT_ROLE.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Projet",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="project_memberships",
        verbose_name="Utilisateur",
    )

    role = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="project_memberships",
        verbose_name="Rôle sur le projet",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    class Meta:
        db_table = "project_membership"
        ordering = [
            "project",
            "user__last_name",
            "user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "user",
                ],
                name="uq_project_membership_project_user",
            ),
        ]
        verbose_name = "Affectation au projet"
        verbose_name_plural = "Affectations aux projets"

    def clean(self):
        super().clean()

        if (
            self.role_id
            and self.role.catalog_type.code
            != "USER_PROJECT_ROLE"
        ):
            raise ValidationError(
                {
                    "role": (
                        "Le rôle doit appartenir au catalogue "
                        "USER_PROJECT_ROLE."
                    ),
                }
            )

    def __str__(self) -> str:
        return (
            f"{self.project.reference} - "
            f"{self.user} - "
            f"{self.role}"
        )