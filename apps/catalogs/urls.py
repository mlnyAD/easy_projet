

from django.urls import path

from apps.catalogs.incremental_views import (
    create_incremental_value,
)


app_name = "catalogs"

urlpatterns = [
    path(
        "incremental-values/create/",
        create_incremental_value,
        name="incremental-create",
    ),
]