

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render as django_render
from django.template.loader import (
    render_to_string as django_render_to_string,
)

from framework.viewmodel import TreeViewModel


DEFAULT_TREE_TEMPLATE_NAME = "edf/tree/tree.html"
TREE_VIEW_CONTEXT_KEY = "tree_view"


class DjangoTreeRenderer:
    """
    Produit un rendu Django à partir d'un TreeViewModel.

    Le renderer ne construit pas l'arborescence et ne résout pas
    les commandes métier. Il reçoit un ViewModel déjà préparé.
    """

    __slots__ = ("_template_name",)

    def __init__(
        self,
        template_name: str = DEFAULT_TREE_TEMPLATE_NAME,
    ) -> None:
        self._template_name = self._validate_template_name(
            template_name,
        )

    @property
    def template_name(self) -> str:
        """Retourne le nom du template par défaut."""
        return self._template_name

    def render(
        self,
        *,
        request: HttpRequest,
        view_model: TreeViewModel,
        template_name: str | None = None,
        context: Mapping[str, Any] | None = None,
        status: int | None = None,
    ) -> HttpResponse:
        """Retourne une réponse HTTP contenant l'arborescence."""
        self._validate_request(request)
        self._validate_view_model(view_model)
        self._validate_status(status)

        return django_render(
            request=request,
            template_name=self._resolve_template_name(
                template_name,
            ),
            context=self._build_context(
                view_model=view_model,
                context=context,
            ),
            status=status,
        )

    def render_to_string(
        self,
        *,
        request: HttpRequest,
        view_model: TreeViewModel,
        template_name: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> str:
        """Retourne uniquement le HTML de l'arborescence."""
        self._validate_request(request)
        self._validate_view_model(view_model)

        return django_render_to_string(
            template_name=self._resolve_template_name(
                template_name,
            ),
            context=self._build_context(
                view_model=view_model,
                context=context,
            ),
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
        view_model: TreeViewModel,
        context: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if context is None:
            additional_context: dict[str, Any] = {}
        else:
            if not isinstance(context, Mapping):
                raise TypeError(
                    "La propriété 'context' doit être un Mapping."
                )

            if TREE_VIEW_CONTEXT_KEY in context:
                raise ValueError(
                    f"La clé {TREE_VIEW_CONTEXT_KEY!r} est "
                    "réservée au renderer."
                )

            additional_context = dict(context)

        return {
            **additional_context,
            TREE_VIEW_CONTEXT_KEY: view_model,
        }

    @staticmethod
    def _validate_request(request: object) -> None:
        if not isinstance(request, HttpRequest):
            raise TypeError(
                "La propriété 'request' doit être une instance "
                "de HttpRequest."
            )

    @staticmethod
    def _validate_view_model(view_model: object) -> None:
        if not isinstance(view_model, TreeViewModel):
            raise TypeError(
                "La propriété 'view_model' doit être une instance "
                "de TreeViewModel."
            )

    @staticmethod
    def _validate_template_name(template_name: object) -> str:
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

    @staticmethod
    def _validate_status(status: object) -> None:
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