

from __future__ import annotations

import json

from django.core.exceptions import ValidationError
from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from apps.catalogs.exceptions import (
    CatalogInactiveError,
    CatalogNotEditableError,
    CatalogNotFoundError,
    CatalogNotIncrementalError,
    CatalogValueAlreadyExistsError,
)
from apps.catalogs.services import CatalogService


def _build_value_code(label: str) -> str:
    """
    Construit un code technique stable à partir du libellé.

    Exemple :
        Chef d'équipe -> CHEF_D_EQUIPE
    """
    return slugify(label).replace("-", "_").upper()


@require_POST
def create_incremental_value(
    request: HttpRequest,
) -> JsonResponse:
    """
    Crée une valeur dans un catalogue éditable et incrémental.
    """
    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return JsonResponse(
            {
                "success": False,
                "error": "La requête est invalide.",
            },
            status=400,
        )

    catalog_code = str(
        payload.get("catalog_code", "")
    ).strip()

    label = str(
        payload.get("label", "")
    ).strip()

    if not catalog_code:
        return JsonResponse(
            {
                "success": False,
                "error": "Le catalogue est obligatoire.",
            },
            status=400,
        )

    if not label:
        return JsonResponse(
            {
                "success": False,
                "error": "Le libellé est obligatoire.",
            },
            status=400,
        )

    value_code = _build_value_code(label)

    if not value_code:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Le libellé ne permet pas de construire "
                    "un code valide."
                ),
            },
            status=400,
        )

    try:
        value = CatalogService.create_value(
            catalog_code=catalog_code,
            code=value_code,
            label=label,
        )
    except CatalogValueAlreadyExistsError:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Une valeur portant ce libellé "
                    "existe déjà."
                ),
            },
            status=409,
        )
    except CatalogNotFoundError:
        return JsonResponse(
            {
                "success": False,
                "error": "Le catalogue demandé n'existe pas.",
            },
            status=404,
        )
    except CatalogInactiveError:
        return JsonResponse(
            {
                "success": False,
                "error": "Le catalogue est inactif.",
            },
            status=400,
        )
    except CatalogNotEditableError:
        return JsonResponse(
            {
                "success": False,
                "error": "Le catalogue n'est pas modifiable.",
            },
            status=403,
        )
    except CatalogNotIncrementalError:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Ce catalogue n'autorise pas "
                    "l'ajout depuis un formulaire."
                ),
            },
            status=403,
        )
    except ValidationError as error:
        return JsonResponse(
            {
                "success": False,
                "error": "; ".join(error.messages),
            },
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "value": {
                "id": str(value.pk),
                "code": value.code,
                "label": value.label,
            },
        },
        status=201,
    )