

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import ExternalIntegration


@admin.register(ExternalIntegration)
class ExternalIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "client_environment",
        "service_type",
        "provider",
        "connection_status",
        "priority",
        "is_active",
    )

    list_filter = (
        "is_active",
        "service_type",
        "provider",
        "connection_status",
    )

    search_fields = (
        "code",
        "name",
        "client_environment__company__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "client_environment",
        "service_type",
        "priority",
        "name",
    )

    list_select_related = (
        "client_environment",
        "client_environment__company",
        "service_type",
        "provider",
        "connection_status",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Rattachement",
            {
                "fields": (
                    "client_environment",
                ),
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "service_type",
                    "provider",
                    "connection_status",
                ),
            },
        ),
        (
            "Identification",
            {
                "fields": (
                    "code",
                    "name",
                    "is_active",
                ),
            },
        ),
        (
            "Orchestration",
            {
                "fields": (
                    "priority",
                ),
            },
        ),
        (
            "Configuration technique",
            {
                "fields": (
                    "configuration",
                    "credential_reference",
                ),
            },
        ),
        (
            "Traçabilité",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )