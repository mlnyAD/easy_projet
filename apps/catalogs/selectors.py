

from django.db.models import QuerySet

from apps.catalogs.exceptions import (
    CatalogNotFoundError,
    CatalogValueNotFoundError,
)
from apps.catalogs.models import CatalogType, CatalogValue

from django.db.models import Max

def get_catalog_by_code(
    catalog_code: str,
) -> CatalogType:
    """
    Retourne un catalogue à partir de son code.

    Lève CatalogNotFoundError si le catalogue n'existe pas.
    """
    try:
        return CatalogType.objects.get(code=catalog_code)
    except CatalogType.DoesNotExist as error:
        raise CatalogNotFoundError(catalog_code) from error


def list_catalog_values(
    catalog: CatalogType,
    *,
    active_only: bool = True,
) -> QuerySet[CatalogValue]:
    """
    Retourne les valeurs d'un catalogue, dans leur ordre d'affichage.
    """
    queryset = CatalogValue.objects.filter(
        catalog_type=catalog,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset.order_by(
        "sort_order",
        "label",
        "code",
    )


def get_catalog_value_by_code(
    catalog: CatalogType,
    value_code: str,
) -> CatalogValue:
    """
    Retourne une valeur à partir de son code.

    Lève CatalogValueNotFoundError si la valeur n'existe pas
    dans le catalogue demandé.
    """
    try:
        return CatalogValue.objects.get(
            catalog_type=catalog,
            code=value_code,
        )
    except CatalogValue.DoesNotExist as error:
        raise CatalogValueNotFoundError(
            catalog.code,
            value_code,
        ) from error


def get_default_catalog_value(
    catalog: CatalogType,
    *,
    active_only: bool = True,
) -> CatalogValue | None:
    """
    Retourne la valeur définie par défaut pour un catalogue.

    Si active_only vaut True, seules les valeurs actives sont considérées.
    """
    queryset = CatalogValue.objects.filter(
        catalog_type=catalog,
        is_default=True,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset.first()


def catalog_value_exists(
    catalog: CatalogType,
    value_code: str,
    *,
    active_only: bool = True,
) -> bool:
    """
    Indique si une valeur existe dans un catalogue.
    """
    queryset = CatalogValue.objects.filter(
        catalog_type=catalog,
        code=value_code,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset.exists()

def get_next_sort_order(
    catalog: CatalogType,
) -> int:
    """
    Retourne le prochain ordre d'affichage disponible.
    """
    maximum = (
        CatalogValue.objects
        .filter(catalog_type=catalog)
        .aggregate(
            maximum=Max("sort_order")
        )["maximum"]
    )

    if maximum is None:
        return 10

    return maximum + 10

def get_next_sort_order(
    catalog: CatalogType,
) -> int:
    """
    Retourne le prochain ordre d'affichage disponible
    pour les valeurs d'un catalogue.
    """
    maximum = (
        CatalogValue.objects
        .filter(catalog_type=catalog)
        .aggregate(maximum=Max("sort_order"))
        .get("maximum")
    )

    if maximum is None:
        return 10

    return maximum + 10