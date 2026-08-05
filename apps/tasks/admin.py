

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "work_package",
        "code",
        "name",
        "status",
        "effective_start_date",
        "effective_end_date",
        "planned_workload_hours",
        "remaining_workload_hours",
        "progress_percent",
        "is_active",
    )

    list_filter = (
        "is_active",
        "status",
        "work_package",
    )

    search_fields = (
        "code",
        "name",
        "description",
        "work_package__code",
        "work_package__name",
        "work_package__project__reference",
        "work_package__project__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "work_package",
        "code",
        "name",
    )

    list_select_related = (
        "work_package",
        "work_package__project",
        "status",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Rattachement",
            {
                "fields": (
                    "work_package",
                    "status",
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
                    "is_active",
                ),
            },
        ),
        (
            "Planning",
            {
                "fields": (
                    "planned_start_date",
                    "planned_end_date",
                    "updated_start_date",
                    "updated_end_date",
                    "planned_workload_hours",
                    "remaining_workload_hours",
                    "progress_percent",
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