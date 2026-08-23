

from __future__ import annotations

from typing import BinaryIO

from django.db import transaction

from apps.documents.models import (
    Document,
    DocumentFolder,
    DocumentHistory,
)
from apps.documents.storage import (
    DocumentStorage,
    get_document_storage,
)
from apps.users.models import User

from .version_service import DocumentVersionService
from .template_service import DocumentTemplateService
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    """
    Service métier principal de création documentaire.

    Il orchestre :
    - la création du Document ;
    - la création de la première version ;
    - la mise à jour de current_version ;
    - l'historisation.

    Le stockage physique reste délégué à DocumentStorage.
    """

    def __init__(
        self,
        storage: DocumentStorage | None = None,
        template_service: DocumentTemplateService | None = None,
    ) -> None:
        self.storage = (
            storage
            or get_document_storage()
        )

        self.version_service = DocumentVersionService(
            storage=self.storage
        )

        self.template_service = (
            template_service
            or DocumentTemplateService()
        )
    
    def create_document(
        self,
        *,
        project,
        folder: DocumentFolder,
        title: str,
        document_format: str,
        document_type,
        status,
        lifecycle,
        user: User,
        is_doe: bool = False,
    ) -> Document:
        """
        Crée un nouveau document bureautique à partir
        d'un modèle technique Easy Projet.

        La création produit immédiatement la version 1.
        """

        definition = self.template_service.get_definition(
            document_format
        )

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError(
                "Le titre du document ne peut pas être vide."
            )

        if folder.project_id != project.pk:
            raise ValueError(
                "Le dossier documentaire doit appartenir au projet."
            )

        extension = definition["extension"]

        if normalized_title.lower().endswith(
            extension.lower()
        ):
            original_filename = normalized_title
        else:
            original_filename = (
                f"{normalized_title}{extension}"
            )

        with self.template_service.open_template(
            document_format
        ) as content:

            with transaction.atomic():

                document = Document.objects.create(
                    project=project,
                    folder=folder,
                    title=normalized_title,
                    document_type=document_type,
                    status=status,
                    lifecycle=lifecycle,
                    is_doe=is_doe,
                    created_by=user,
                )

                version = self.version_service.create_version(
                    document=document,
                    content=content,
                    original_filename=original_filename,
                    mime_type=definition["mime_type"],
                    user=user,
                )

                DocumentHistory.objects.create(
                    document=document,
                    version=version,
                    action=DocumentHistory.Action.CREATED,
                    user=user,
                    details=(
                        f"Création du document "
                        f"{version.original_filename}."
                    ),
                )

                return document
        
    def import_document(
        self,
        *,
        project,
        folder: DocumentFolder,
        title: str,
        document_type,
        status,
        lifecycle,
        content: BinaryIO,
        original_filename: str,
        mime_type: str,
        user: User,
        is_doe: bool = False,
    ) -> Document:
        """
        Importe un fichier externe dans Easy Projet.

        L'import crée :
        - le Document ;
        - la version 1 ;
        - l'historique d'import.
        """

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError(
                "Le titre du document ne peut pas être vide."
            )

        if folder.project_id != project.pk:
            raise ValueError(
                "Le dossier documentaire doit appartenir au projet."
            )

        with transaction.atomic():

            document = Document.objects.create(
                project=project,
                folder=folder,
                title=normalized_title,
                document_type=document_type,
                status=status,
                lifecycle=lifecycle,
                is_doe=is_doe,
                created_by=user,
            )

            version = (
                self.version_service.create_version(
                    document=document,
                    content=content,
                    original_filename=original_filename,
                    mime_type=mime_type,
                    user=user,
                )
            )

            DocumentHistory.objects.create(
                document=document,
                version=version,
                action=DocumentHistory.Action.IMPORTED,
                user=user,
                details=(
                    f"Import du fichier "
                    f"{version.original_filename}."
                ),
            )

            return document
        
    @staticmethod
    @transaction.atomic
    def rename_document(
        *,
        document: Document,
        title: str,
        user: User,
    ) -> Document:
        """
        Renomme l'identité fonctionnelle d'un document.

        Les versions existantes restent immuables :
        original_filename et contenu physique
        ne sont pas modifiés.
        """

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError(
                "Le titre du document ne peut pas être vide."
            )

        if normalized_title == document.title:
            return document

        old_title = document.title

        document.title = normalized_title

        document.save(
            update_fields=[
                "title",
                "updated_at",
            ]
        )

        DocumentHistory.objects.create(
            document=document,
            version=document.current_version,
            action=DocumentHistory.Action.RENAMED,
            user=user,
            details=(
                f'Renommage de "{old_title}" '
                f'en "{normalized_title}".'
            ),
        )

        return document
    
    @staticmethod
    @transaction.atomic
    def move_document(
        *,
        document: Document,
        destination: DocumentFolder,
        user: User,
    ) -> Document:
        """
        Déplace un document dans un autre dossier
        du même projet.

        Les versions et le stockage physique
        restent inchangés.
        """

        if (
            destination.project_id
            != document.project_id
        ):
            raise ValueError(
                "Le dossier de destination doit "
                "appartenir au même projet."
            )

        if (
            destination.pk
            == document.folder_id
        ):
            return document

        source = document.folder

        document.folder = destination

        document.full_clean()

        document.save(
            update_fields=[
                "folder",
                "updated_at",
            ]
        )

        DocumentHistory.objects.create(
            document=document,
            version=document.current_version,
            action=DocumentHistory.Action.MOVED,
            user=user,
            details=(
                f'Déplacement de "{source.name}" '
                f'vers "{destination.name}".'
            ),
        )

        return document
    
    @transaction.atomic
    def copy_document(
        self,
        *,
        document: Document,
        destination: DocumentFolder,
        user: User,
        title: str | None = None,
    ) -> Document:
        """
        Copie un document dans un autre dossier du même projet.

        La copie :
        - crée un nouveau Document ;
        - reprend les métadonnées métier du document source ;
        - copie uniquement la version courante ;
        - crée une nouvelle V1 ;
        - n'hérite pas de l'historique du document source.
        """

        if (
            destination.project_id
            != document.project_id
        ):
            raise ValueError(
                "Le dossier de destination doit "
                "appartenir au même projet."
            )

        source_version = (
            document.current_version
        )

        if source_version is None:
            raise ValueError(
                "Le document source ne possède "
                "aucune version courante."
            )

        normalized_title = (
            title.strip()
            if title is not None
            else document.title
        )

        if not normalized_title:
            raise ValueError(
                "Le titre du document copié "
                "ne peut pas être vide."
            )

        if not self.storage.exists(
            source_version.storage_key
        ):
            raise ValueError(
                "Le fichier source est introuvable."
            )

        with self.storage.open(
            source_version.storage_key
        ) as source_content:

            copied_document = (
                Document.objects.create(
                    project=document.project,
                    folder=destination,
                    title=normalized_title,
                    document_type=document.document_type,
                    status=document.status,
                    lifecycle=document.lifecycle,
                    is_doe=document.is_doe,
                    created_by=user,
                )
            )

            copied_version = (
                self.version_service.create_version(
                    document=copied_document,
                    content=source_content,
                    original_filename=(
                        source_version.original_filename
                    ),
                    mime_type=(
                        source_version.mime_type
                    ),
                    user=user,
                )
            )

        DocumentHistory.objects.create(
            document=copied_document,
            version=copied_version,
            action=DocumentHistory.Action.COPIED,
            user=user,
            details=(
                f'Copie depuis "{document.title}".'
            ),
        )

        return copied_document
    
    def delete_document(
        self,
        *,
        document: Document,
    ) -> None:
        """
        Supprime définitivement un document.

        La suppression comprend :
        - le Document ;
        - ses DocumentVersion ;
        - son historique ;
        - ses favoris par cascade ;
        - les fichiers physiques associés.

        Les fichiers physiques sont supprimés uniquement
        après validation de la transaction PostgreSQL.
        """

        with transaction.atomic():

            locked_document = (
                Document.objects
                .select_for_update()
                .get(pk=document.pk)
            )

            storage_keys = list(
                locked_document.versions
                .values_list(
                    "storage_key",
                    flat=True,
                )
            )

            # La version courante référence une DocumentVersion
            # avec PROTECT. On libère donc explicitement
            # cette référence avant la suppression en cascade.
            if (
                locked_document.current_version_id
                is not None
            ):
                locked_document.current_version = None

                locked_document.save(
                    update_fields=[
                        "current_version",
                        "updated_at",
                    ]
                )

            locked_document.delete()

            transaction.on_commit(
                lambda: self._delete_storage_files(
                    storage_keys
                )
            )

    def _delete_storage_files(
        self,
        storage_keys: list[str],
    ) -> None:
        """
        Supprime les fichiers physiques après commit BD.

        Une erreur de nettoyage physique ne doit pas
        remettre en cause une transaction déjà validée.
        """

        for storage_key in storage_keys:

            try:
                self.storage.delete(
                    storage_key
                )

            except Exception:
                logger.exception(
                    "Impossible de supprimer le fichier "
                    "documentaire %s.",
                    storage_key,
                )