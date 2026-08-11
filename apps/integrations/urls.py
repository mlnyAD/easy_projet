

from django.urls import path

from .views import (
    ExternalIntegrationCreateView,
    ExternalIntegrationListView,
    ExternalIntegrationUpdateView,
)


app_name = "integrations"


urlpatterns = [
    path(
        "",
        ExternalIntegrationListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        ExternalIntegrationCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        ExternalIntegrationUpdateView.as_view(),
        name="update",
    ),
]