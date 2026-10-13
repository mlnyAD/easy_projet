

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from apps.catalogs import bootstrap  # noqa: F401
from framework.bootstrap.executor import (
    BootstrapExecutor,
)
from framework.bootstrap.registry import (
    BootstrapNotFoundError,
    registry,
)


class Command(BaseCommand):
    """
    Crée ou met à jour les catalogues de référence.
    """

    help = (
        "Synchronise les types et valeurs de catalogue "
        "définis dans les données applicatives."
    )

    def handle(self, *args, **options):
        try:
            executor = BootstrapExecutor(registry)

            executor.execute("catalogs")
        except BootstrapNotFoundError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(
                "Synchronisation des catalogues terminée."
            )
        )