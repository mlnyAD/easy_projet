

class CatalogError(Exception):
    """Classe de base des erreurs du domaine des catalogues."""


class CatalogNotFoundError(CatalogError):
    """Le catalogue demandé n'existe pas."""

    def __init__(self, catalog_code: str) -> None:
        self.catalog_code = catalog_code
        super().__init__(
            f"Le catalogue '{catalog_code}' n'existe pas."
        )


class CatalogInactiveError(CatalogError):
    """Le catalogue demandé est inactif."""

    def __init__(self, catalog_code: str) -> None:
        self.catalog_code = catalog_code
        super().__init__(
            f"Le catalogue '{catalog_code}' est inactif."
        )


class CatalogNotEditableError(CatalogError):
    """Le catalogue ne peut pas être modifié."""

    def __init__(self, catalog_code: str) -> None:
        self.catalog_code = catalog_code
        super().__init__(
            f"Le catalogue '{catalog_code}' n'est pas modifiable."
        )


class CatalogNotIncrementalError(CatalogError):
    """Le catalogue ne peut pas être enrichi depuis un écran métier."""

    def __init__(self, catalog_code: str) -> None:
        self.catalog_code = catalog_code
        super().__init__(
            f"Le catalogue '{catalog_code}' n'est pas incrémental."
        )


class CatalogValueNotFoundError(CatalogError):
    """La valeur demandée n'existe pas dans le catalogue."""

    def __init__(
        self,
        catalog_code: str,
        value_code: str,
    ) -> None:
        self.catalog_code = catalog_code
        self.value_code = value_code
        super().__init__(
            f"La valeur '{value_code}' n'existe pas "
            f"dans le catalogue '{catalog_code}'."
        )


class CatalogValueInactiveError(CatalogError):
    """La valeur demandée est inactive."""

    def __init__(
        self,
        catalog_code: str,
        value_code: str,
    ) -> None:
        self.catalog_code = catalog_code
        self.value_code = value_code
        super().__init__(
            f"La valeur '{value_code}' du catalogue "
            f"'{catalog_code}' est inactive."
        )


class CatalogValueAlreadyExistsError(CatalogError):
    """Une valeur portant ce code existe déjà."""

    def __init__(
        self,
        catalog_code: str,
        value_code: str,
    ) -> None:
        self.catalog_code = catalog_code
        self.value_code = value_code
        super().__init__(
            f"La valeur '{value_code}' existe déjà "
            f"dans le catalogue '{catalog_code}'."
        )


class CatalogSystemValueProtectedError(CatalogError):
    """Une valeur système ne peut pas subir l'opération demandée."""

    def __init__(
        self,
        catalog_code: str,
        value_code: str,
    ) -> None:
        self.catalog_code = catalog_code
        self.value_code = value_code
        super().__init__(
            f"La valeur système '{value_code}' du catalogue "
            f"'{catalog_code}' est protégée."
        )


class CatalogDefaultValueError(CatalogError):
    """L'opération est incompatible avec la valeur par défaut."""

    def __init__(
        self,
        catalog_code: str,
        value_code: str,
    ) -> None:
        self.catalog_code = catalog_code
        self.value_code = value_code
        super().__init__(
            f"La valeur par défaut '{value_code}' du catalogue "
            f"'{catalog_code}' ne peut pas subir cette opération."
        )


class CatalogValidationError(CatalogError):
    """Les données fournies ne respectent pas les règles du catalogue."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)