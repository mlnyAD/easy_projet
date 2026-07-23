

from framework.bootstrap.base import Bootstrap
from framework.bootstrap.registry import BootstrapRegistry


class BootstrapExecutor:
    """Exécute les bootstraps enregistrés."""

    def __init__(self, registry: BootstrapRegistry) -> None:
        self._registry = registry

    def execute(self, name: str) -> None:
        bootstrap = self._registry.get(name)
        self._run(bootstrap)

    def execute_all(self) -> None:
        for bootstrap in self._registry.all():
            self._run(bootstrap)

    def _run(self, bootstrap: Bootstrap) -> None:
        bootstrap.run()