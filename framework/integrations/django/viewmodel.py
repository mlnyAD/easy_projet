from __future__ import annotations

from datetime import datetime
from typing import Any

from django.utils import timezone

from framework.viewmodel.builder import ListViewModelBuilder


class DjangoListViewModelBuilder(ListViewModelBuilder):
    """
    Construit un modèle de liste destiné aux templates Django.

    Les dates et heures stockées par Django sont en UTC lorsque USE_TZ
    est activé. Elles sont converties dans le fuseau actif uniquement
    pour leur affichage.
    """

    def _format_display_value(
        self,
        *,
        value: Any,
        data_type: str,
    ) -> str:
        if (
            isinstance(value, datetime)
            and timezone.is_aware(value)
        ):
            value = timezone.localtime(value)

        return super()._format_display_value(
            value=value,
            data_type=data_type,
        )
