

from django.core.management.base import BaseCommand, CommandError

from framework.bootstrap import BootstrapExecutor, registry

from framework.bootstrap import Bootstrap


class TestBootstrap(Bootstrap):
    name = "test"

    def run(self) -> None:
        print("Bootstrap de test exécuté")


registry.register(TestBootstrap())


class Command(BaseCommand):
    help = "Initialise les données de référence d'Easy Projet."

    def add_arguments(self, parser):
        parser.add_argument(
            "bootstrap_name",
            nargs="?",
            help="Nom du bootstrap à exécuter.",
        )

    def handle(self, *args, **options):
        bootstrap_name = options.get("bootstrap_name")
        executor = BootstrapExecutor(registry)

        try:
            if bootstrap_name:
                executor.execute(bootstrap_name)
            else:
                executor.execute_all()
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS("Bootstrap terminé avec succès.")
        )