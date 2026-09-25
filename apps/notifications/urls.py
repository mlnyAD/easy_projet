from django.urls import path

from apps.notifications.views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationOpenView,
)


app_name = "notifications"


urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path(
        "mark-all-read/",
        NotificationMarkAllReadView.as_view(),
        name="mark-all-read",
    ),
    path("<uuid:pk>/open/", NotificationOpenView.as_view(), name="open"),
]
