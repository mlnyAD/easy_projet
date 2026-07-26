
        
from apps.catalogs.models import CatalogValue


class CatalogService:
    """Service d'accès aux catalogues métier."""

    @staticmethod
    def get_choices(catalog_code: str) -> list[tuple[str, str]]:
        """
        Retourne les valeurs actives d'un catalogue au format attendu
        par les champs de choix Django.

        Exemple :
            [
                ("uuid-1", "CDI"),
                ("uuid-2", "CDD"),
            ]
        """
        normalized_code = catalog_code.strip().upper()

        queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code=normalized_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

        return [
            (str(value.pk), value.label)
            for value in queryset
        ]