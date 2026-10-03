

from __future__ import annotations

import shutil
import zipfile
from collections import defaultdict
from pathlib import PurePosixPath
from tempfile import SpooledTemporaryFile

from apps.documents.models import Document, DocumentFolder
from apps.documents.storage import (
    DocumentStorage,
    get_document_storage,
)


class DocumentFolderArchiveService:
    """
    Construit une archive ZIP à partir d'un dossier documentaire.

    L'archive contient tous les sous-dossiers et les versions
    courantes des documents qu'ils contiennent.
    """

    def __init__(
        self,
        storage: DocumentStorage | None = None,
    ) -> None:
        self.storage = (
            storage
            or get_document_storage()
        )

    def create_archive(
        self,
        *,
        folder: DocumentFolder,
    ) -> SpooledTemporaryFile:
        """
        Retourne une archive ZIP positionnée au début du flux.
        """

        folders_by_id = self._get_subtree_folders(
            folder=folder,
        )

        documents = (
            Document.objects
            .filter(
                folder_id__in=folders_by_id,
                current_version__isnull=False,
            )
            .select_related(
                "folder",
                "current_version",
            )
            .order_by(
                "folder__sort_order",
                "folder__name",
                "title",
            )
        )

        archive = SpooledTemporaryFile(
            max_size=10 * 1024 * 1024,
            mode="w+b",
        )

        used_names: set[str] = set()

        with zipfile.ZipFile(
            archive,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as zip_file:
            for document in documents:
                version = document.current_version

                if not self.storage.exists(
                    version.storage_key
                ):
                    raise ValueError(
                        "Le fichier documentaire "
                        f'"{version.original_filename}" '
                        "est introuvable."
                    )

                archive_name = self._get_archive_name(
                    document=document,
                    root_folder=folder,
                    folders_by_id=folders_by_id,
                    used_names=used_names,
                )

                with self.storage.open(
                    version.storage_key
                ) as source:
                    with zip_file.open(
                        archive_name,
                        mode="w",
                    ) as destination:
                        shutil.copyfileobj(
                            source,
                            destination,
                        )

        archive.seek(0)

        return archive

    @staticmethod
    def _get_subtree_folders(
        *,
        folder: DocumentFolder,
    ) -> dict[object, DocumentFolder]:
        """
        Retourne le dossier demandé et tous ses descendants.
        """

        project_folders = list(
            DocumentFolder.objects
            .filter(
                project=folder.project,
                is_active=True,
            )
            .only(
                "id",
                "parent_id",
                "name",
            )
        )

        children_by_parent: dict[
            object | None,
            list[DocumentFolder],
        ] = defaultdict(list)

        for project_folder in project_folders:
            children_by_parent[
                project_folder.parent_id
            ].append(project_folder)

        folders_by_id = {
            folder.pk: folder,
        }

        pending = [folder.pk]

        while pending:
            parent_id = pending.pop()

            for child in children_by_parent[parent_id]:
                folders_by_id[child.pk] = child
                pending.append(child.pk)

        return folders_by_id

    def _get_archive_name(
        self,
        *,
        document: Document,
        root_folder: DocumentFolder,
        folders_by_id: dict[object, DocumentFolder],
        used_names: set[str],
    ) -> str:
        """
        Construit un chemin ZIP sûr et unique.
        """

        folder_parts = self._get_folder_parts(
            folder=document.folder,
            root_folder=root_folder,
            folders_by_id=folders_by_id,
        )

        filename = self._safe_path_component(
            document.current_version.original_filename
        )

        candidate = str(
            PurePosixPath(
                *folder_parts,
                filename,
            )
        )

        unique_name = candidate
        sequence = 2

        while unique_name in used_names:
            path = PurePosixPath(candidate)

            unique_name = str(
                path.with_name(
                    f"{path.stem} ({sequence}){path.suffix}"
                )
            )

            sequence += 1

        used_names.add(unique_name)

        return unique_name

    def _get_folder_parts(
        self,
        *,
        folder: DocumentFolder,
        root_folder: DocumentFolder,
        folders_by_id: dict[object, DocumentFolder],
    ) -> list[str]:
        """
        Retourne le chemin relatif incluant le dossier racine.
        """

        parts = []
        current = folder

        while current is not None:
            parts.append(
                self._safe_path_component(current.name)
            )

            if current.pk == root_folder.pk:
                break

            current = folders_by_id.get(
                current.parent_id
            )

        parts.reverse()

        return parts

    @staticmethod
    def _safe_path_component(value: str) -> str:
        """
        Empêche qu'un nom de dossier ou de fichier sorte du ZIP.
        """

        normalized = (
            value
            .replace("\\", "/")
            .split("/")[-1]
            .strip()
        )

        if normalized in {
            "",
            ".",
            "..",
        }:
            return "sans-nom"

        return normalized