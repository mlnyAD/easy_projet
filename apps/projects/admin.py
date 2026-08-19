

from django.contrib import admin

from .models import (
    Project,
    ProjectExternalParticipant,
    ProjectMembership,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "name",
        "company",
        "project_manager",
        "status",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = (
        "company",
        "status",
        "is_active",
    )

    search_fields = (
        "reference",
        "name",
        "contract_reference",
    )

    ordering = (
        "reference",
        "name",
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "user",
        "role",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
    )

    search_fields = (
        "project__reference",
        "project__name",
        "user__last_name",
        "user__first_name",
        "user__email",
    )

    ordering = (
        "project",
        "user__last_name",
        "user__first_name",
    )


@admin.register(ProjectExternalParticipant)
class ProjectExternalParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "last_name",
        "first_name",
        "email",
        "company_name",
        "access_level",
        "is_active",
    )

    list_filter = (
        "access_level",
        "is_active",
    )

    search_fields = (
        "project__reference",
        "project__name",
        "last_name",
        "first_name",
        "email",
        "company_name",
    )

    ordering = (
        "project",
        "last_name",
        "first_name",
    )