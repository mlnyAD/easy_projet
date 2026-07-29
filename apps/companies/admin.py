
    
from django.contrib import admin

from common.constants import DEFAULT_PAGE_SIZE

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "email",
        "phone",
        "is_active",
    )

    list_filter = (
        "is_active",
        "city",
    )

    search_fields = (
        "name",
        "city",
        "email",
    )

    ordering = ("name",)

    list_per_page = DEFAULT_PAGE_SIZE