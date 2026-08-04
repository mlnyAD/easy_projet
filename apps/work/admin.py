

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import WorkPackage


@admin.register(WorkPackage)
class WorkPackageAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "code",
        "name",
        "manager",
        "status",
        "start_date",
        "end_date",
        "planned_workload_hours",
        "is_active",
    )

    list_filter = (
        "is_active",
        "status",
        "project",
    )

    search_fields = (
        "code",
        "name",
        "description",
        "project__reference",
        "project__name",
        "manager__last_name",
        "manager__first_name",
        "manager__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "project",
        "code",
        "name",
    )

    list_select_related = (
        "project",
        "manager",
        "status",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Rattachement",
            {
                "fields": (
                    "project",
                ),
            },
        ),
        (
            "Identification",
            {
                "fields": (
                    "code",
                    "name",
                    "description",
                ),
            },
        ),
        (
            "Pilotage",
            {
                "fields": (
                    "status",
                    "manager",
                    "is_active",
                ),
            },
        ),
        (
            "Planning",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "planned_workload_hours",
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