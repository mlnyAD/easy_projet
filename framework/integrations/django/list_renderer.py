

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render as django_render
from django.template.loader import render_to_string as django_render_to_string

from framework.viewmodel import ListViewModel


DEFAULT_LIST_TEMPLATE_NAME = "edf/list/list.html"
LIST_VIEW_CONTEXT_KEY = "list_view"


class DjangoListRenderer:
    """
    Produit un rendu Django à partir d'un ListViewModel.

    Le renderer ne construit pas les données, ne trie pas, ne pagine pas
    et ne modifie jamais le ViewModel reçu.
    """

    __slots__ = ("_template_name",)

    def __init__(
        self,
        template_name: str = DEFAULT_LIST_TEMPLATE_NAME,
    ) -> None:
        self._template_name = self._validate_template_name(
            template_name,
        )

    @property
    def template_name(self) -> str:
        """Retourne le nom du template par défaut du renderer."""
        return self._template_name

    def render(
        self,
        *,
        request: HttpRequest,
        view_model: ListViewModel,
        template_name: str | None = None,
        context: Mapping[str, Any] | None = None,
        status: int | None = None,
    ) -> HttpResponse:
        """
        Retourne une réponse HTTP contenant le rendu de la liste.
        """
        self._validate_request(request)
        self._validate_view_model(view_model)
        self._validate_status(status)

        resolved_template = self._resolve_template_name(
            template_name,
        )
        final_context = self._build_context(
            view_model=view_model,
            context=context,
        )

        return django_render(
            request=request,
            template_name=resolved_template,
            context=final_context,
            status=status,
        )

    def render_to_string(
        self,
        *,
        request: HttpRequest,
        view_model: ListViewModel,
        template_name: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> str:
        """
        Retourne uniquement la chaîne HTML produite par Django.
        """
        self._validate_request(request)
        self._validate_view_model(view_model)

        resolved_template = self._resolve_template_name(
            template_name,
        )
        final_context = self._build_context(
            view_model=view_model,
            context=context,
        )

        return django_render_to_string(
            template_name=resolved_template,
            context=final_context,
            request=request,
        )

    def _resolve_template_name(
        self,
        template_name: str | None,
    ) -> str:
        if template_name is None:
            return self._template_name

        return self._validate_template_name(template_name)

    def _build_context(
        self,
        *,
        view_model: ListViewModel,
        context: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if context is None:
            additional_context: dict[str, Any] = {}
        else:
            if not isinstance(context, Mapping):
                raise TypeError(
                    "La propriété 'context' doit être un Mapping."
                )

            if LIST_VIEW_CONTEXT_KEY in context:
                raise ValueError(
                    f"La clé {LIST_VIEW_CONTEXT_KEY!r} est réservée "
                    "au renderer."
                )

            additional_context = dict(context)

        return {
            **additional_context,
            LIST_VIEW_CONTEXT_KEY: view_model,
        }

    def _validate_request(
        self,
        request: object,
    ) -> None:
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "La propriété 'request' doit être une instance "
                "de HttpRequest."
            )

    def _validate_view_model(
        self,
        view_model: object,
    ) -> None:
        if not isinstance(view_model, ListViewModel):
            raise TypeError(
                "La propriété 'view_model' doit être une instance "
                "de ListViewModel."
            )

    def _validate_template_name(
        self,
        template_name: object,
    ) -> str:
        if not isinstance(template_name, str):
            raise TypeError(
                "Le nom du template doit être une chaîne "
                "de caractères."
            )

        normalized_name = template_name.strip()

        if not normalized_name:
            raise ValueError(
                "Le nom du template ne peut pas être vide."
            )

        return normalized_name

    def _validate_status(
        self,
        status: object,
    ) -> None:
        if status is None:
            return

        if isinstance(status, bool) or not isinstance(status, int):
            raise TypeError(
                "La propriété 'status' doit être un entier."
            )

        if not 100 <= status <= 599:
            raise ValueError(
                "La propriété 'status' doit être comprise "
                "entre 100 et 599."
            )