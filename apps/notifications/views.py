from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
        )


class NotificationOpenView(LoginRequiredMixin, View):
    """Marque une notification comme lue puis ouvre son objet cible."""

    def get(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user,
        )

        NotificationService.mark_as_read(
            notification=notification,
        )

        if url_has_allowed_host_and_scheme(
            notification.target_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(notification.target_url)

        return redirect(reverse("notifications:list"))


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            read_at__isnull=True,
        ).update(read_at=timezone.now())

        return redirect(reverse("notifications:list"))
