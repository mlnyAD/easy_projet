

from django.contrib import admin

from .models import (
    Task,
    TaskAssignment,
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "work_package",
        "status",
        "start_date",
        "end_date",
        "planned_workload_hours",
        "remaining_workload_hours",
        "progress_percent",
        "is_active",
    )

    list_filter = (
        "status",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "work_package__code",
        "work_package__name",
        "work_package__project__reference",
        "work_package__project__name",
    )

    ordering = (
        "work_package",
        "code",
        "name",
    )


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "user",
        "role",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
    )

    search_fields = (
        "task__code",
        "task__name",
        "user__last_name",
        "user__first_name",
        "user__email",
    )

    ordering = (
        "task",
        "user__last_name",
        "user__first_name",
    )