

from dataclasses import asdict

from framework.bootstrap import Bootstrap, registry

from apps.catalogs.data.definitions import CATALOG_DEFINITIONS
from apps.catalogs.data.values import CATALOG_VALUE_DEFINITIONS
from apps.catalogs.services import CatalogService


class CatalogBootstrap(Bootstrap):
    name = "catalogs"
    version = "1.0"
    dependencies = ()

    def run(self) -> None:
        print(f"Catalogues à charger : {len(CATALOG_DEFINITIONS)}")
        print(f"Valeurs à charger : {len(CATALOG_VALUE_DEFINITIONS)}")

        for definition in CATALOG_DEFINITIONS:
            CatalogService.upsert_type(**asdict(definition))

        for value_definition in CATALOG_VALUE_DEFINITIONS:
            data = asdict(value_definition)

            if "catalog" in data:
                data["catalog_code"] = data.pop("catalog")

            # Champ présent dans la définition mais non géré
            # actuellement par CatalogService.upsert_value().
            data.pop("level", None)

            CatalogService.upsert_value(**data)


registry.register(CatalogBootstrap())