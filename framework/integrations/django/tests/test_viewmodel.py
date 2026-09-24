from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import TestCase, override_settings
from django.utils import timezone

from framework.integrations.django.viewmodel import (
    DjangoListViewModelBuilder,
)


@override_settings(
    TIME_ZONE="Europe/Paris",
    USE_TZ=True,
)
class DjangoListViewModelBuilderTests(TestCase):
    def test_aware_datetime_is_displayed_in_active_timezone(self):
        value = datetime(
            2026,
            9,
            29,
            7,
            30,
            tzinfo=ZoneInfo("UTC"),
        )

        with timezone.override("Europe/Paris"):
            display_value = (
                DjangoListViewModelBuilder()
                ._format_display_value(
                    value=value,
                    data_type="datetime",
                )
            )

        self.assertEqual(
            display_value,
            "29/09/2026 09:30",
        )

    def test_naive_datetime_is_not_converted(self):
        value = datetime(2026, 9, 29, 9, 30)

        display_value = (
            DjangoListViewModelBuilder()
            ._format_display_value(
                value=value,
                data_type="datetime",
            )
        )

        self.assertEqual(
            display_value,
            "29/09/2026 09:30",
        )
