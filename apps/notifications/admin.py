from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "project",
        "kind",
        "read_at",
        "created_at",
    )
    list_filter = ("kind", "read_at")
    search_fields = ("title", "body", "user__email")
    readonly_fields = ("created_at", "updated_at", "read_at")
