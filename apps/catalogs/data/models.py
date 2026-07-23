

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogDefinition:
    """Définition d'un type de catalogue."""

    code: str
    label: str
    description: str = ""

    is_hierarchical: bool = False
    is_editable: bool = False
    is_incremental: bool = False
    is_active: bool = True

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True, slots=True)
class CatalogValueDefinition:
    """Définition d'une valeur de catalogue."""

    catalog: str

    code: str
    label: str
    description: str = ""

    level: int = 0
    sort_order: int = 0

    is_default: bool = False
    is_system: bool = True
    is_active: bool = True

    def __str__(self) -> str:
        return f"{self.catalog}.{self.code}"