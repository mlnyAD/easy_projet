from django.test import TestCase, override_settings
from django.urls import reverse

from apps.companies.models import Company
from apps.notifications.models import Notification
from apps.users.models import User


@override_settings(DEV_AUTO_LOGIN=False)
class NotificationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        company = Company.objects.create(name="Société vue notifications")
        cls.user = User.objects.create(
            company=company,
            email="notification-view@example.com",
            first_name="Victor",
            last_name="Vue",
        )
        cls.notification = Notification.objects.create(
            user=cls.user,
            kind=Notification.Kind.MEETING_INVITATION,
            source_key="meeting-invitation:view-test",
            title="Invitation à une réunion",
            target_url="/meetings/",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_list_displays_only_current_user_notifications(self):
        response = self.client.get(reverse("notifications:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invitation à une réunion")

    def test_open_marks_notification_as_read_and_redirects(self):
        response = self.client.get(
            reverse("notifications:open", kwargs={"pk": self.notification.pk})
        )

        self.assertRedirects(response, "/meetings/")

        self.notification.refresh_from_db()
        self.assertIsNotNone(self.notification.read_at)
