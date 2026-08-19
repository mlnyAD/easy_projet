

from django.urls import path

from .views import PlanningHomeView


app_name = "planning"


urlpatterns = [
    path(
        "",
        PlanningHomeView.as_view(),
        name="home",
    ),
]