

from django.urls import path

from .views import (
    RiskCreateView,
    RiskListByProjectView,
    RiskListView,
    RiskUpdateView,
)


app_name = "risks"

urlpatterns = [
    path(
        "",
        RiskListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        RiskCreateView.as_view(),
        name="create",
    ),
    path(
        "projects/<uuid:project_pk>/",
        RiskListByProjectView.as_view(),
        name="list-by-project",
    ),
    path(
        "<uuid:pk>/edit/",
        RiskUpdateView.as_view(),
        name="update",
    ),
]