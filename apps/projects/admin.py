

from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "name",
        "company",
        "project_manager",
        "status",
        "contractual_start_date",
        "contractual_end_date",
        "is_active",
    )

    list_filter = (
        "is_active",
        "status",
        "project_type",
        "company",
    )

    search_fields = (
        "reference",
        "name",
        "contract_reference",
        "city",
        "company__name",
        "owner_company__name",
        "designer_company__name",
        "project_manager__last_name",
        "project_manager__first_name",
        "project_manager__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "reference",
        "name",
    )

    list_select_related = (
        "company",
        "project_manager",
        "status",
        "project_type",
    )

    list_per_page = DEFAULT_PAGE_SIZE

    fieldsets = (
        (
            "Identification",
            {
                "fields": (
                    "reference",
                    "name",
                    "description",
                    "company",
                    "project_manager",
                    "status",
                    "is_active",
                ),
            },
        ),
        (
            "Client et contrat",
            {
                "fields": (
                    "owner_company",
                    "designer_company",
                    "project_type",
                    "contract_reference",
                    "comments",
                ),
            },
        ),
        (
            "Localisation",
            {
                "fields": (
                    "address_1",
                    "address_2",
                    "address_3",
                    "postal_code",
                    "city",
                    "country",
                ),
            },
        ),
        (
            "Charge et planning",
            {
                "fields": (
                    "planned_workload_hours",
                    "contractual_start_date",
                    "contractual_end_date",
                    "start_date_review",
                    "end_date_review",
                    "receipt_date_init",
                    "receipt_date_review",
                    "delivery_date_init",
                    "delivery_date_review",
                ),
            },
        ),
        (
            "Données commerciales",
            {
                "fields": (
                    "amount_quote_ht",
                    "amount_quote_ttc",
                    "amount_order_ht",
                    "amount_order_ttc",
                    "currency",
                    "budget_comments",
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