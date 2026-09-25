from django.test import TestCase
from django.utils import timezone

from apps.companies.models import Company
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService
from apps.users.models import User


class NotificationServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        company = Company.objects.create(name="Société notifications")
        cls.user = User.objects.create(
            company=company,
            email="notification@example.com",
            first_name="Nora",
            last_name="Notification",
        )

    def test_upsert_renews_existing_notification(self):
        notification = NotificationService.upsert(
            user=self.user,
            project=None,
            kind=Notification.Kind.MEETING_INVITATION,
            source_key="meeting-invitation:test",
            title="Invitation initiale",
            body="Premier créneau",
            target_url="/meetings/test/edit/",
        )
        notification.read_at = timezone.now()
        notification.save(update_fields=("read_at",))

        renewed_notification = NotificationService.upsert(
            user=self.user,
            project=None,
            kind=Notification.Kind.MEETING_INVITATION,
            source_key="meeting-invitation:test",
            title="Invitation modifiée",
            body="Nouveau créneau",
            target_url="/meetings/test/edit/",
        )

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(renewed_notification.pk, notification.pk)
        self.assertEqual(renewed_notification.title, "Invitation modifiée")
        self.assertIsNone(renewed_notification.read_at)
