

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from pathlib import Path

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.document import (
    DOCUMENT_CHECKSUM_LENGTH,
    DOCUMENT_EXTENSION_LENGTH,
    DOCUMENT_FILENAME_LENGTH,
    DOCUMENT_FOLDER_NAME_LENGTH,
    DOCUMENT_HISTORY_ACTION_LENGTH,
    DOCUMENT_HISTORY_DETAILS_LENGTH,
    DOCUMENT_MIME_TYPE_LENGTH,
    DOCUMENT_STORAGE_KEY_LENGTH,
    DOCUMENT_TECHNICAL_TYPE_LENGTH,
    DOCUMENT_TITLE_LENGTH,
)
from common.models import TimeStampedModel


class DocumentFolder(TimeStampedModel):
    """
    Dossier logique de l'arborescence documentaire d'un projet.

    L'arborescence documentaire est indépendante de l'organisation
    physique des fichiers dans le stockage.
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
        related_name="document_folders",
        verbose_name="Projet",
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
        max_length=DOCUMENT_FOLDER_NAME_LENGTH,
        verbose_name="Nom",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Dossier actif",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence de l'arborescence.
        """
        super().clean()

        if (
            self.parent_id is not None
            and self.parent_id == self.pk
        ):
            raise ValidationError(
                {
                    "parent": (
                        "Un dossier ne peut pas être "
                        "son propre parent."
                    ),
                }
            )

        if (
            self.parent_id is not None
            and self.project_id is not None
            and self.parent.project_id
            != self.project_id
        ):
            raise ValidationError(
                {
                    "parent": (
                        "Le dossier parent doit appartenir "
                        "au même projet."
                    ),
                }
            )

        if (
            self.parent_id is not None
            and self._would_create_cycle()
        ):
            raise ValidationError(
                {
                    "parent": (
                        "Ce déplacement créerait une boucle "
                        "dans l'arborescence documentaire."
                    ),
                }
            )

    def _would_create_cycle(self) -> bool:
        """
        Vérifie qu'un dossier ne devient pas descendant
        de l'un de ses propres descendants.
        """

        current = self.parent

        visited = set()

        while current is not None:

            if current.pk == self.pk:
                return True

            if current.pk in visited:
                return True

            visited.add(
                current.pk
            )

            current = current.parent

        return False

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        self.name = self.name.strip()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "document_folder"

        ordering = [
            "project",
            "sort_order",
            "name",
        ]

        verbose_name = "Dossier documentaire"
        verbose_name_plural = "Dossiers documentaires"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "parent",
                    "name",
                ],
                condition=models.Q(
                    parent__isnull=False,
                ),
                name=(
                    "uniq_document_folder_"
                    "name_by_parent"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "project",
                    "name",
                ],
                condition=models.Q(
                    parent__isnull=True,
                ),
                name=(
                    "uniq_document_root_folder_"
                    "name_by_project"
                ),
            ),
        ]

    @property
    def full_path(self) -> str:
        """
        Retourne le chemin logique complet du dossier.
        """

        names = [
            self.name,
        ]

        current = self.parent

        visited = {
            self.pk,
        }

        while current is not None:

            if current.pk in visited:
                break

            visited.add(
                current.pk
            )

            names.append(
                current.name
            )

            current = current.parent

        return " / ".join(
            reversed(names)
        )

    def __str__(self) -> str:
        return self.name


class Document(TimeStampedModel):
    """
    Objet documentaire métier.

    Le Document porte l'identité et les métadonnées du document.

    Le contenu physique est porté par DocumentVersion.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # Rattachement
    # ------------------------------------------------------------------

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Projet",
    )

    folder = models.ForeignKey(
        DocumentFolder,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Dossier",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    title = models.CharField(
        max_length=DOCUMENT_TITLE_LENGTH,
        verbose_name="Titre",
    )

    document_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="document_type_documents",
        verbose_name="Type de document",
    )

    # ------------------------------------------------------------------
    # États
    # ------------------------------------------------------------------

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="document_status_documents",
        verbose_name="Statut métier",
    )

    lifecycle = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="document_lifecycle_documents",
        verbose_name="État GED",
    )

    # ------------------------------------------------------------------
    # Version courante
    # ------------------------------------------------------------------

    current_version = models.ForeignKey(
        "DocumentVersion",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Version courante",
    )

    # ------------------------------------------------------------------
    # DOE
    # ------------------------------------------------------------------

    is_doe = models.BooleanField(
        default=False,
        verbose_name="Sélectionné pour le DOE",
    )

    # ------------------------------------------------------------------
    # Créateur
    # ------------------------------------------------------------------

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_documents",
        verbose_name="Créé par",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence intrinsèque du document.
        """
        super().clean()

        if (
            self.folder_id is not None
            and self.project_id is not None
            and self.folder.project_id
            != self.project_id
        ):
            raise ValidationError(
                {
                    "folder": (
                        "Le dossier documentaire doit "
                        "appartenir au même projet."
                    ),
                }
            )

        if (
            self.current_version_id is not None
            and self.current_version.document_id
            != self.pk
        ):
            raise ValidationError(
                {
                    "current_version": (
                        "La version courante doit appartenir "
                        "à ce document."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        self.title = self.title.strip()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "document"

        ordering = [
            "project",
            "folder",
            "title",
        ]

        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self) -> str:
        return self.title


class DocumentVersion(TimeStampedModel):
    """
    Version physique enregistrée d'un document.

    Une nouvelle version est créée lorsqu'une modification
    effectuée dans un éditeur est effectivement enregistrée.

    Une version existante ne doit pas être modifiée.

    Les métadonnées techniques du fichier sont déterminées
    automatiquement par Easy Projet.
    """

    class TechnicalType(models.TextChoices):
        CAD = (
            "CAD",
            "CAO",
        )

        OFFICE = (
            "OFFICE",
            "Bureautique",
        )

        PDF = (
            "PDF",
            "PDF",
        )

        IMAGE = (
            "IMAGE",
            "Image",
        )

        MEDIA = (
            "MEDIA",
            "Audio / vidéo",
        )

        OTHER = (
            "OTHER",
            "Autre",
        )

    CAD_EXTENSIONS = frozenset(
        {
            ".dwg",
            ".dxf",
            ".dwf",
            ".dgn",
            ".pcf",
        }
    )

    OFFICE_EXTENSIONS = frozenset(
        {
            ".docx",
            ".xlsx",
            ".pptx",
        }
    )

    IMAGE_EXTENSIONS = frozenset(
        {
            ".bmp",
            ".gif",
            ".jpeg",
            ".jpg",
            ".png",
            ".tif",
            ".tiff",
            ".webp",
        }
    )

    MEDIA_EXTENSIONS = frozenset(
        {
            ".avi",
            ".m4a",
            ".mkv",
            ".mov",
            ".mp3",
            ".mp4",
            ".ogg",
            ".wav",
            ".webm",
        }
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="Document",
    )

    version_number = models.PositiveIntegerField(
        editable=False,
        verbose_name="Version",
    )

    original_filename = models.CharField(
        max_length=DOCUMENT_FILENAME_LENGTH,
        verbose_name="Nom du fichier d'origine",
    )

    extension = models.CharField(
        max_length=DOCUMENT_EXTENSION_LENGTH,
        editable=False,
        verbose_name="Extension",
    )

    technical_type = models.CharField(
        max_length=DOCUMENT_TECHNICAL_TYPE_LENGTH,
        choices=TechnicalType.choices,
        editable=False,
        verbose_name="Type technique",
    )

    storage_key = models.CharField(
        max_length=DOCUMENT_STORAGE_KEY_LENGTH,
        unique=True,
        editable=False,
        verbose_name="Clé de stockage",
    )

    mime_type = models.CharField(
        max_length=DOCUMENT_MIME_TYPE_LENGTH,
        blank=True,
        verbose_name="Type MIME",
    )

    file_size = models.PositiveBigIntegerField(
        verbose_name="Taille du fichier",
    )

    checksum = models.CharField(
        max_length=DOCUMENT_CHECKSUM_LENGTH,
        editable=False,
        verbose_name="Empreinte SHA-256",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_document_versions",
        verbose_name="Créé par",
    )

    # ------------------------------------------------------------------
    # Métadonnées techniques
    # ------------------------------------------------------------------

    @classmethod
    def detect_extension(
        cls,
        filename: str,
    ) -> str:
        """
        Détermine automatiquement l'extension normalisée.
        """

        return (
            Path(filename)
            .suffix
            .lower()
        )

    @classmethod
    def detect_technical_type(
        cls,
        *,
        extension: str,
        mime_type: str = "",
    ) -> str:
        """
        Détermine automatiquement la famille technique
        du fichier.

        L'extension est prioritaire pour les formats
        explicitement connus.

        Le type MIME complète la détection pour les
        images et médias.
        """

        normalized_extension = (
            extension
            .strip()
            .lower()
        )

        normalized_mime_type = (
            mime_type
            .strip()
            .lower()
        )

        if (
            normalized_extension
            in cls.CAD_EXTENSIONS
        ):
            return cls.TechnicalType.CAD

        if (
            normalized_extension
            in cls.OFFICE_EXTENSIONS
        ):
            return cls.TechnicalType.OFFICE

        if normalized_extension == ".pdf":
            return cls.TechnicalType.PDF

        if (
            normalized_extension
            in cls.IMAGE_EXTENSIONS
            or normalized_mime_type.startswith(
                "image/"
            )
        ):
            return cls.TechnicalType.IMAGE

        if (
            normalized_extension
            in cls.MEDIA_EXTENSIONS
            or normalized_mime_type.startswith(
                "audio/"
            )
            or normalized_mime_type.startswith(
                "video/"
            )
        ):
            return cls.TechnicalType.MEDIA

        return cls.TechnicalType.OTHER

    def refresh_technical_metadata(
        self,
    ) -> None:
        """
        Recalcule les métadonnées techniques du fichier.

        Cette opération ne demande aucune intervention
        utilisateur.
        """

        self.extension = (
            self.detect_extension(
                self.original_filename
            )
        )

        self.technical_type = (
            self.detect_technical_type(
                extension=self.extension,
                mime_type=self.mime_type,
            )
        )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        Synchronise automatiquement les métadonnées
        techniques avant persistance.
        """

        self.original_filename = (
            self.original_filename
            .strip()
        )

        self.mime_type = (
            self.mime_type
            .strip()
            .lower()
        )

        self.refresh_technical_metadata()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "document_version"

        ordering = [
            "document",
            "version_number",
        ]

        verbose_name = "Version de document"
        verbose_name_plural = "Versions de documents"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "document",
                    "version_number",
                ],
                name=(
                    "uniq_document_"
                    "version_number"
                ),
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.document.title} "
            f"- V{self.version_number}"
        )

class DocumentEditLock(TimeStampedModel):
    """
    Verrou applicatif d'édition d'un document.

    Un document ne peut être verrouillé que par un seul
    utilisateur à la fois.

    Le verrou mémorise la version qui était courante lors
    de sa prise ainsi que sa date d'expiration.

    La logique d'acquisition, de renouvellement et de
    libération est portée par DocumentEditLockService.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name="edit_lock",
        verbose_name="Document",
    )

    version = models.ForeignKey(
        DocumentVersion,
        on_delete=models.CASCADE,
        related_name="edit_locks",
        verbose_name="Version",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="document_edit_locks",
        verbose_name="Utilisateur",
    )

    expires_at = models.DateTimeField(
        verbose_name="Expiration",
    )

    class Meta:
        db_table = "document_edit_lock"

        ordering = [
            "expires_at",
        ]

        verbose_name = "Verrou d'édition documentaire"
        verbose_name_plural = (
            "Verrous d'édition documentaire"
        )

    def clean(self) -> None:
        """
        Vérifie que la version verrouillée appartient
        au document verrouillé.
        """
        super().clean()

        if (
            self.version_id is not None
            and self.document_id is not None
            and self.version.document_id
            != self.document_id
        ):
            raise ValidationError(
                {
                    "version": (
                        "La version verrouillée doit "
                        "appartenir au document."
                    ),
                }
            )

    def __str__(self) -> str:
        return (
            f"{self.document} - "
            f"{self.user}"
        )
        
class DocumentHistory(TimeStampedModel):
    """
    Trace une opération métier réalisée sur un document.
    """

    class Action(models.TextChoices):
        CREATED = (
            "CREATED",
            "Création",
        )

        IMPORTED = (
            "IMPORTED",
            "Import",
        )

        OPENED = (
            "OPENED",
            "Ouverture",
        )

        VERSION_CREATED = (
            "VERSION_CREATED",
            "Nouvelle version",
        )

        RENAMED = (
            "RENAMED",
            "Renommage",
        )

        MOVED = (
            "MOVED",
            "Déplacement",
        )

        COPIED = (
            "COPIED",
            "Copie",
        )

        DOWNLOADED = (
            "DOWNLOADED",
            "Téléchargement",
        )

        SHARED = (
            "SHARED",
            "Partage",
        )

        ARCHIVED = (
            "ARCHIVED",
            "Archivage",
        )

        RESTORED = (
            "RESTORED",
            "Restauration",
        )

        TRASHED = (
            "TRASHED",
            "Mise en corbeille",
        )

        SIGNED = (
            "SIGNED",
            "Signature",
        )

        DOE_SELECTED = (
            "DOE_SELECTED",
            "Sélection DOE",
        )

        DOE_UNSELECTED = (
            "DOE_UNSELECTED",
            "Retrait DOE",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Document",
    )

    version = models.ForeignKey(
        DocumentVersion,
        on_delete=models.SET_NULL,
        related_name="history_entries",
        null=True,
        blank=True,
        verbose_name="Version",
    )

    action = models.CharField(
        max_length=DOCUMENT_HISTORY_ACTION_LENGTH,
        choices=Action.choices,
        verbose_name="Action",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="document_history_entries",
        verbose_name="Utilisateur",
    )

    details = models.TextField(
        max_length=DOCUMENT_HISTORY_DETAILS_LENGTH,
        blank=True,
        verbose_name="Détails",
    )

    def clean(self) -> None:
        """
        Vérifie que la version historisée appartient
        au document concerné.
        """
        super().clean()

        if (
            self.version_id is not None
            and self.document_id is not None
            and self.version.document_id
            != self.document_id
        ):
            raise ValidationError(
                {
                    "version": (
                        "La version historisée doit "
                        "appartenir au document."
                    ),
                }
            )

    class Meta:
        db_table = "document_history"

        ordering = [
            "-created_at",
        ]

        verbose_name = "Historique documentaire"
        verbose_name_plural = "Historique documentaire"

    def __str__(self) -> str:
        return (
            f"{self.document.title} - "
            f"{self.get_action_display()}"
        )
        
class DocumentFavorite(TimeStampedModel):
    """
    Document placé dans les favoris personnels
    d'un utilisateur.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="document_favorites",
        verbose_name="Utilisateur",
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Document",
    )

    class Meta:
        db_table = "document_favorite"

        ordering = [
            "-created_at",
        ]

        verbose_name = "Document favori"
        verbose_name_plural = "Documents favoris"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "document",
                ],
                name=(
                    "uniq_document_favorite_"
                    "user_document"
                ),
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.user} - "
            f"{self.document}"
        )