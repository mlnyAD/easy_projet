

from abc import ABC, abstractmethod


class Bootstrap(ABC):
    """Contrat de base d'un bootstrap applicatif."""

    name: str = ""
    version: str = "1.0"
    dependencies: tuple[str, ...] = ()

    @abstractmethod
    def run(self) -> None:
        """Exécute l'initialisation du module."""
        raise NotImplementedError