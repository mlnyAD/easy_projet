

from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO

from .base import DocumentStorage


class FileSystemDocumentStorage(DocumentStorage):
    """
    Stockage documentaire sur système de fichiers local.
    """

    def __init__(
        self,
        root: Path | str,
    ) -> None:
        self.root = Path(root).resolve()

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        storage_key: str,
        content: BinaryIO,
    ) -> None:
        path = self.get_path(storage_key)

        if path.exists():
            raise FileExistsError(
                f"Le fichier existe déjà : {storage_key}"
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open("xb") as destination:
            shutil.copyfileobj(
                content,
                destination,
            )

    def open(
        self,
        storage_key: str,
    ) -> BinaryIO:
        path = self.get_path(storage_key)

        return path.open("rb")

    def exists(
        self,
        storage_key: str,
    ) -> bool:
        return self.get_path(storage_key).is_file()

    def delete(
        self,
        storage_key: str,
    ) -> None:
        path = self.get_path(storage_key)

        if not path.exists():
            return

        path.unlink()

        self._remove_empty_parents(
            path.parent
        )

    def get_path(
        self,
        storage_key: str,
    ) -> Path:
        """
        Résout une clé de stockage en empêchant toute sortie
        du répertoire racine.
        """

        key = storage_key.strip()

        if not key:
            raise ValueError(
                "La clé de stockage ne peut pas être vide."
            )

        path = (
            self.root
            / Path(key)
        ).resolve()

        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(
                "Clé de stockage invalide."
            ) from exc

        if path == self.root:
            raise ValueError(
                "La clé de stockage doit désigner un fichier."
            )

        return path

    def _remove_empty_parents(
        self,
        directory: Path,
    ) -> None:
        """
        Supprime les répertoires devenus vides jusqu'à la racine
        du stockage, sans jamais supprimer celle-ci.
        """

        current = directory

        while current != self.root:

            try:
                current.rmdir()
            except OSError:
                break

            current = current.parent