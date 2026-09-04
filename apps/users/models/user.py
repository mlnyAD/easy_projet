

from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company

from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_INITIALS_LENGTH,
    USER_LAST_NAME_LENGTH,
    USER_MOBILE_LENGTH,
    USER_PHONE_LENGTH,
    USER_THEME_LENGTH,
)
from common.models.base import TimeStampedModel

from .managers import UserManager

class Theme(models.TextChoices):
    SYSTEM = "system", _("Système")
    LIGHT = "light", _("Clair")
    DARK = "dark", _("Sombre")

class User(
    AbstractBaseUser,
    PermissionsMixin,
    TimeStampedModel,
):
    """
    Utilisateur Easy Projet.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_("Identifiant"),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "last_name",
        "first_name",
    ]
    
    # ------------------------------------------------------------------
    # Identité
    # ------------------------------------------------------------------

    last_name = models.CharField(
        max_length=USER_LAST_NAME_LENGTH,
        verbose_name=_("Nom"),
    )

    first_name = models.CharField(
        max_length=USER_FIRST_NAME_LENGTH,
        verbose_name=_("Prénom"),
    )

    initials = models.CharField(
        max_length=USER_INITIALS_LENGTH,
        editable=False,
        verbose_name=_("Initiales"),
    )

    photo = models.ImageField(
        upload_to="users/photos/",
        blank=True,
        null=True,
        verbose_name=_("Photo"),
    )    
    # ------------------------------------------------------------------
    # Coordonnées
    # ------------------------------------------------------------------

    email = models.EmailField(
        max_length=USER_EMAIL_LENGTH,
        unique=True,
        verbose_name=_("Adresse électronique"),
    )

    phone = models.CharField(
        max_length=USER_PHONE_LENGTH,
        blank=True,
        verbose_name=_("Téléphone"),
    )

    mobile = models.CharField(
        max_length=USER_MOBILE_LENGTH,
        blank=True,
        verbose_name=_("Téléphone mobile"),
    )    
    # ------------------------------------------------------------------
    # Rattachement
    # ------------------------------------------------------------------

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name=_("Société"),
    )

    employment_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="employment_type_users",
        null=True,
        blank=True,
        verbose_name=_("Type d'emploi"),
    )

    job = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="job_users",
        null=True,
        blank=True,
        verbose_name=_("Métier"),
    )

    global_role = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="global_role_users",
        verbose_name=_("Rôle global"),
    )

    access_level = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="access_level_users",
        verbose_name=_("Niveau d'accès"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Accès à l'administration"),
    )
    
    # ------------------------------------------------------------------
    # Authentification
    # ------------------------------------------------------------------

    must_change_password = models.BooleanField(
        default=False,
        verbose_name=_(
            "Changement de mot de passe obligatoire"
        ),
    )

    temporary_password_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_(
            "Mot de passe provisoire envoyé le"
        ),
    )

    # ------------------------------------------------------------------
    # Préférences
    # ------------------------------------------------------------------

    theme = models.CharField(
        max_length=USER_THEME_LENGTH,
        choices=Theme.choices,
        default=Theme.SYSTEM,
        verbose_name=_("Thème"),
    )
            
    class Meta:
        db_table = "user"
        ordering = [
            "last_name",
            "first_name",
        ]
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name}"

    def save(self, *args, **kwargs):
        """
        Normalisation avant enregistrement.
        """

        if self.email:
            self.email = self.email.strip().lower()

        self.last_name = self.last_name.strip()
        self.first_name = self.first_name.strip()

        initials = ""

        if self.first_name:
            initials += self.first_name[0].upper()

        if self.last_name:
            initials += self.last_name[0].upper()

        self.initials = initials

        super().save(*args, **kwargs)