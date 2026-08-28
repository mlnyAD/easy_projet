
        
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.users.models import User
from common.constants.project import (
    PROJECT_ADDRESS_LENGTH,
    PROJECT_AMOUNT_DECIMAL_PLACES,
    PROJECT_AMOUNT_MAX_DIGITS,
    PROJECT_CITY_LENGTH,
    PROJECT_COMMENT_LENGTH,
    PROJECT_CONTRACT_REFERENCE_LENGTH,
    PROJECT_COORDINATE_DECIMAL_PLACES,
    PROJECT_COORDINATE_MAX_DIGITS,
    PROJECT_COUNTRY_LENGTH,
    PROJECT_CURRENCY_LENGTH,
    PROJECT_DEFAULT_AMOUNT,
    PROJECT_DEFAULT_CURRENCY,
    PROJECT_DEFAULT_WORKLOAD_HOURS,
    PROJECT_DESCRIPTION_LENGTH,
    PROJECT_NAME_LENGTH,
    PROJECT_POSTAL_CODE_LENGTH,
    PROJECT_REFERENCE_LENGTH,
)
from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_LAST_NAME_LENGTH,
)
from common.models import TimeStampedModel


def project_photo_upload_to(
    instance,
    filename: str,
) -> str:
    """
    Construit le chemin de stockage de la photo principale
    d'un projet.
    """
    return (
        f"projects/{instance.pk}/photo/{filename}"
    )

class Project(TimeStampedModel):
    """
    Projet contractuel et opérationnel géré dans Easy Projet.

    Le projet décrit ce qui a été vendu et accepté par le client.
    Les coûts internes, prix de revient et marges relèvent du module
    financier et ne sont pas stockés dans ce modèle.

    Les dates initiales constituent la référence de planification.
    Les dates courantes représentent le planning actuellement validé.
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

    project_photo = models.ImageField(
        upload_to=project_photo_upload_to,
        null=True,
        blank=True,
        verbose_name="Photo du projet",
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
        verbose_name="Latitude",
    )

    longitude = models.DecimalField(
        max_digits=PROJECT_COORDINATE_MAX_DIGITS,
        decimal_places=PROJECT_COORDINATE_DECIMAL_PLACES,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Longitude",
    )

    # ------------------------------------------------------------------
    # Charge et planning
    # ------------------------------------------------------------------

    planned_workload_hours = models.PositiveIntegerField(
        default=PROJECT_DEFAULT_WORKLOAD_HOURS,
        verbose_name="Charge prévisionnelle (h)",
    )

    # ------------------------------------------------------------------
    # Dates de référence
    # ------------------------------------------------------------------

    initial_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Début initial",
    )

    initial_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin initiale",
    )

    # ------------------------------------------------------------------
    # Dates courantes
    # ------------------------------------------------------------------

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Début",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin",
    )

    # ------------------------------------------------------------------
    # Jalons - réception
    # ------------------------------------------------------------------

    initial_receipt_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Réception initiale",
    )

    receipt_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Réception",
    )

    # ------------------------------------------------------------------
    # Jalons - livraison
    # ------------------------------------------------------------------

    initial_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Livraison initiale",
    )

    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Livraison",
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

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence intrinsèque des dates du projet.

        Les dates initiales et les dates courantes constituent deux
        couples indépendants. Les dates initiales servent de référence,
        tandis que les dates courantes portent le planning validé.
        """
        super().clean()

        if (
            self.initial_start_date is not None
            and self.initial_end_date is not None
            and self.initial_end_date < self.initial_start_date
        ):
            raise ValidationError(
                {
                    "initial_end_date": (
                        "La fin initiale ne peut pas être antérieure "
                        "au début initial."
                    ),
                }
            )

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "La date de fin ne peut pas être antérieure "
                        "à la date de début."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs):
        """
        Normalise et sécurise le rattachement du projet.

        Lorsqu'une date courante n'est pas renseignée, elle est
        initialisée avec la date initiale correspondante.

        Si l'adresse d'un projet existant est modifiée, les coordonnées
        géographiques sont invalidées.
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
        # Initialisation des dates courantes
        # --------------------------------------------------------------

        initialized_fields = set()

        if (
            self.start_date is None
            and self.initial_start_date is not None
        ):
            self.start_date = self.initial_start_date
            initialized_fields.add("start_date")

        if (
            self.end_date is None
            and self.initial_end_date is not None
        ):
            self.end_date = self.initial_end_date
            initialized_fields.add("end_date")

        if (
            self.receipt_date is None
            and self.initial_receipt_date is not None
        ):
            self.receipt_date = self.initial_receipt_date
            initialized_fields.add("receipt_date")

        if (
            self.delivery_date is None
            and self.initial_delivery_date is not None
        ):
            self.delivery_date = self.initial_delivery_date
            initialized_fields.add("delivery_date")

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

                    initialized_fields.update(
                        {
                            "latitude",
                            "longitude",
                        }
                    )

        # --------------------------------------------------------------
        # update_fields
        # --------------------------------------------------------------

        update_fields = kwargs.get("update_fields")

        if (
            update_fields is not None
            and initialized_fields
        ):
            update_fields = set(update_fields)
            update_fields.update(initialized_fields)
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


class ProjectExternalParticipant(TimeStampedModel):
    """
    Intervenant externe ponctuel associé à un projet.

    L'intervenant n'est pas nécessairement un utilisateur
    Easy Projet.

    Son niveau d'accès doit appartenir au catalogue
    PROJECT_EXTERNAL_ACCESS.

    Lorsqu'il est converti en utilisateur Easy Projet,
    converted_user référence l'utilisateur créé.
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
        related_name="external_participants",
        verbose_name="Projet",
    )

    last_name = models.CharField(
        max_length=USER_LAST_NAME_LENGTH,
        verbose_name="Nom",
    )

    first_name = models.CharField(
        max_length=USER_FIRST_NAME_LENGTH,
        verbose_name="Prénom",
    )

    email = models.EmailField(
        max_length=USER_EMAIL_LENGTH,
        verbose_name="Adresse électronique",
    )

    company_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Société",
    )

    access_level = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="project_external_participants",
        verbose_name="Niveau d'accès",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    converted_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="converted_external_participations",
        null=True,
        blank=True,
        verbose_name="Utilisateur créé",
    )

    class Meta:
        db_table = "project_external_participant"
        ordering = [
            "project",
            "last_name",
            "first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "email",
                ],
                name=(
                    "uq_project_external_participant_"
                    "project_email"
                ),
            ),
        ]
        verbose_name = "Intervenant externe au projet"
        verbose_name_plural = (
            "Intervenants externes aux projets"
        )

    def clean(self):
        super().clean()

        if (
            self.access_level_id
            and self.access_level.catalog_type.code
            != "PROJECT_EXTERNAL_ACCESS"
        ):
            raise ValidationError(
                {
                    "access_level": (
                        "Le niveau d'accès doit appartenir au "
                        "catalogue PROJECT_EXTERNAL_ACCESS."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normalise les informations avant enregistrement.
        """
        self.last_name = self.last_name.strip().upper()
        self.first_name = self.first_name.strip()

        if self.email:
            self.email = self.email.strip().lower()

        self.company_name = self.company_name.strip()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.project.reference} - "
            f"{self.last_name} {self.first_name}"
        )