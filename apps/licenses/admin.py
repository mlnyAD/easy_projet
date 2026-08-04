

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "company_name",
        "status",
        "project_capacity",
        "granted_at",
        "expiration_date",
    )

    list_filter = (
        "status",
        "granted_at",
    )

    search_fields = (
        "reference",
        "client_environment__company__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-granted_at",
        "reference",
    )

    list_select_related = (
        "client_environment",
        "status",
    )

    list_per_page = DEFAULT_PAGE_SIZE