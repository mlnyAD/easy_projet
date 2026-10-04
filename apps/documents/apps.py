

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "apps.documents"

    verbose_name = (
        "Gestion documentaire"
    )

    def ready(self) -> None:
        from apps.documents.integrations import registry
        from apps.documents.integrations.providers import (
            CadViewerAdapter,
            DocumensoAdapter,
            OnlyOfficeAdapter,
        )

        integrations = (
            OnlyOfficeAdapter(),
            CadViewerAdapter(),
            DocumensoAdapter(),
        )

        for integration in integrations:
            try:
                registry.get(
                    integration.provider_code
                )
            except LookupError:
                registry.register(
                    integration
                )