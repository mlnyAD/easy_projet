

from __future__ import annotations

from common.constants import (
    DEFAULT_PAGE_SIZE,
    PAGE_SIZE_VALUES,
)


class EPListPaginationMixin:
    """
    Gestion générique de la pagination des listes Easy Projet.

    Le nombre de lignes par page peut être choisi par l'utilisateur
    parmi les valeurs autorisées par le framework.
    """

    paginate_by = DEFAULT_PAGE_SIZE

    page_size_parameter = "page_size"

    page_size_values = PAGE_SIZE_VALUES

    def get_paginate_by(self, queryset):
        raw_page_size = self.request.GET.get(
            self.page_size_parameter,
            "",
        )

        try:
            page_size = int(raw_page_size)
        except (
            TypeError,
            ValueError,
        ):
            return self.paginate_by

        if page_size not in self.page_size_values:
            return self.paginate_by

        return page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        context["page_sizes"] = (
            self.page_size_values
        )

        return context