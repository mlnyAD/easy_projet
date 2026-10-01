

from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse


class LoginRequiredMiddlewareTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(
        self,
    ):
        response = self.client.get(
            reverse("companies:list"),
        )

        expected_url = (
            f"{reverse('users:login')}?"
            f"{urlencode({'next': reverse('companies:list')})}"
        )

        self.assertRedirects(
            response,
            expected_url,
            fetch_redirect_response=False,
        )