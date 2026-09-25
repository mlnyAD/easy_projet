from apps.notifications.models import Notification


def notification_context(request):
    """Expose les informations nécessaires à la cloche du bandeau."""

    if not request.user.is_authenticated:
        return {}

    notifications = Notification.objects.filter(
        user=request.user,
    )

    return {
        "notification_unread_count": notifications.filter(
            read_at__isnull=True,
        ).count(),
        "topbar_notifications": notifications[:5],
    }
