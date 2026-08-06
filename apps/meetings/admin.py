

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import Meeting, MeetingParticipant


class MeetingParticipantInline(admin.TabularInline):
    model = MeetingParticipant
    extra = 0
    fields = (
        "participant",
        "external_name",
        "external_email",
        "invitation_response",
        "is_active",
    )
    show_change_link = True


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "subject",
        "project",
        "organizer",
        "status",
        "scheduled_at",
        "duration_hours",
        "location",
        "is_active",
    )

    list_filter = (
        "is_active",
        "status",
        "scheduled_at",
    )

    search_fields = (
        "reference",
        "subject",
        "location",
        "notes",
        "comments",
        "project__reference",
        "project__name",
        "organizer__last_name",
        "organizer__first_name",
        "organizer__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "project",
        "-scheduled_at",
        "reference",
    )

    list_select_related = (
        "project",
        "organizer",
        "status",
    )

    autocomplete_fields = (
        "project",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    inlines = (
        MeetingParticipantInline,
    )

    fieldsets = (
        (
            "Rattachement",
            {
                "fields": (
                    "project",
                    "organizer",
                    "status",
                ),
            },
        ),
        (
            "Identification",
            {
                "fields": (
                    "reference",
                    "subject",
                    "is_active",
                ),
            },
        ),
        (
            "Organisation",
            {
                "fields": (
                    "scheduled_at",
                    "duration_hours",
                    "location",
                ),
            },
        ),
        (
            "Informations",
            {
                "fields": (
                    "notes",
                    "comments",
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


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "meeting",
        "display_name",
        "participant",
        "external_name",
        "external_email",
        "invitation_response",
        "is_active",
    )

    list_filter = (
        "is_active",
        "invitation_response",
    )

    search_fields = (
        "meeting__reference",
        "meeting__subject",
        "participant__last_name",
        "participant__first_name",
        "participant__email",
        "external_name",
        "external_email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "meeting",
        "participant",
        "external_name",
    )

    list_select_related = (
        "meeting",
        "participant",
        "invitation_response",
    )

    autocomplete_fields = (
        "meeting",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Réunion",
            {
                "fields": (
                    "meeting",
                ),
            },
        ),
        (
            "Participant",
            {
                "fields": (
                    "participant",
                    "external_name",
                    "external_email",
                ),
            },
        ),
        (
            "Invitation",
            {
                "fields": (
                    "invitation_response",
                    "is_active",
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