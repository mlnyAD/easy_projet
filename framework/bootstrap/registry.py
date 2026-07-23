

from framework.bootstrap.base import Bootstrap


class BootstrapRegistryError(RuntimeError):
    """Erreur liée au registre des bootstraps."""


class BootstrapAlreadyRegisteredError(BootstrapRegistryError):
    """Bootstrap déjà enregistré."""


class BootstrapNotFoundError(BootstrapRegistryError):
    """Bootstrap introuvable."""


class BootstrapRegistry:
    """Registre des bootstraps disponibles."""

    def __init__(self) -> None:
        self._bootstraps: dict[str, Bootstrap] = {}

    def register(self, bootstrap: Bootstrap) -> None:
        name = bootstrap.name.strip()

        if not name:
            raise BootstrapRegistryError(
                "Le nom du bootstrap est obligatoire."
            )

        if name in self._bootstraps:
            raise BootstrapAlreadyRegisteredError(
                f"Le bootstrap '{name}' est déjà enregistré."
            )

        self._bootstraps[name] = bootstrap

    def get(self, name: str) -> Bootstrap:
        try:
            return self._bootstraps[name]
        except KeyError as exc:
            raise BootstrapNotFoundError(
                f"Le bootstrap '{name}' est introuvable."
            ) from exc

    def all(self) -> tuple[Bootstrap, ...]:
        return tuple(self._bootstraps.values())


registry = BootstrapRegistry()