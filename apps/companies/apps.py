
    
from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.companies"
    verbose_name = "Sociétés"

    def ready(self) -> None:
        from apps.companies import bootstrap  # noqa: F401