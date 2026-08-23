

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class DocumentStorage(ABC):
    """
    Interface d'accès au stockage physique des documents.

    Le stockage manipule uniquement des fichiers et des clés de stockage.
    Il ne connaît ni les modèles Django, ni les éditeurs externes,
    ni la logique de versionnement.
    """

    @abstractmethod
    def save(
        self,
        storage_key: str,
        content: BinaryIO,
    ) -> None:
        """
        Enregistre le contenu sous la clé fournie.

        Une clé existante ne doit pas être écrasée silencieusement.
        """
        raise NotImplementedError

    @abstractmethod
    def open(
        self,
        storage_key: str,
    ) -> BinaryIO:
        """
        Ouvre un fichier existant en lecture binaire.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        storage_key: str,
    ) -> bool:
        """
        Indique si la clé existe dans le stockage.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        storage_key: str,
    ) -> None:
        """
        Supprime physiquement un fichier.
        """
        raise NotImplementedError

    @abstractmethod
    def get_path(
        self,
        storage_key: str,
    ) -> Path:
        """
        Retourne le chemin physique correspondant à une clé.

        Cette méthode est principalement utile au stockage local.
        """
        raise NotImplementedError