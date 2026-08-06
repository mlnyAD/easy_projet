

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import Risk


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "title",
        "project",
        "owner",
        "risk_type",
        "criticality",
        "status",
        "occurrence_date",
        "closure_date",
        "is_active",
    )

    list_filter = (
        "is_active",
        "risk_type",
        "criticality",
        "status",
        "origin",
        "risk_class",
        "severity",
        "probability",
    )

    search_fields = (
        "reference",
        "title",
        "description",
        "planned_actions",
        "project__reference",
        "project__name",
        "owner__last_name",
        "owner__first_name",
        "owner__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "project",
        "reference",
        "title",
    )

    list_select_related = (
        "project",
        "owner",
        "origin",
        "risk_type",
        "risk_class",
        "impact",
        "severity",
        "probability",
        "status",
        "criticality",
        "review_frequency",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Rattachement",
            {
                "fields": (
                    "project",
                    "owner",
                ),
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "origin",
                    "risk_type",
                    "risk_class",
                    "impact",
                    "severity",
                    "probability",
                    "status",
                    "criticality",
                    "review_frequency",
                ),
            },
        ),
        (
            "Identification",
            {
                "fields": (
                    "reference",
                    "title",
                    "description",
                    "is_active",
                ),
            },
        ),
        (
            "Évaluation",
            {
                "fields": (
                    "occurrence_date",
                    "closure_date",
                    "estimated_cost",
                    "last_review_date",
                    "planned_actions",
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