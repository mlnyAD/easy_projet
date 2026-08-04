

"""
Dictionnaire métier de l'entité Project.
"""

from common.constants.project import (
    PROJECT_ADDRESS_LENGTH,
    PROJECT_AMOUNT_DECIMAL_PLACES,
    PROJECT_AMOUNT_MAX_DIGITS,
    PROJECT_CITY_LENGTH,
    PROJECT_COMMENT_LENGTH,
    PROJECT_CONTRACT_REFERENCE_LENGTH,
    PROJECT_COUNTRY_LENGTH,
    PROJECT_CURRENCY_LENGTH,
    PROJECT_DEFAULT_AMOUNT,
    PROJECT_DEFAULT_CURRENCY,
    PROJECT_DEFAULT_WORKLOAD_HOURS,
    PROJECT_DESCRIPTION_LENGTH,
    PROJECT_NAME_LENGTH,
    PROJECT_POSTAL_CODE_LENGTH,
    PROJECT_REFERENCE_LENGTH,
)


PROJECT_DICTIONARY = {
    "entity": {
        "name": "project",
        "label": "Projet",
        "label_plural": "Projets",
        "description": (
            "Projet contractuel et opérationnel géré dans Easy Projet."
        ),
    },

    "fields": {
        # ------------------------------------------------------------------
        # Identification
        # ------------------------------------------------------------------

        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "reference": {
            "label": "Référence",
            "data_type": "string",
            "required": True,
            "unique": True,
            "max_length": PROJECT_REFERENCE_LENGTH,
        },

        "name": {
            "label": "Nom du projet",
            "data_type": "string",
            "required": True,
            "max_length": PROJECT_NAME_LENGTH,
        },

        "description": {
            "label": "Description",
            "data_type": "text",
            "required": False,
            "max_length": PROJECT_DESCRIPTION_LENGTH,
        },

        "company": {
            "label": "Société responsable",
            "data_type": "uuid",
            "required": True,
            "reference": "company",
        },

        "project_manager": {
            "label": "Chef de projet",
            "data_type": "uuid",
            "required": False,
            "reference": "user",
        },

        "status": {
            "label": "Statut",
            "data_type": "uuid",
            "required": True,
            "catalog": "PROJECT_STATUS",
        },

        "is_active": {
            "label": "Projet actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },

        # ------------------------------------------------------------------
        # Client et contrat
        # ------------------------------------------------------------------

        "owner_company": {
            "label": "Maître d’ouvrage",
            "data_type": "uuid",
            "required": False,
            "reference": "company",
        },

        "designer_company": {
            "label": "Maître d’œuvre",
            "data_type": "uuid",
            "required": False,
            "reference": "company",
        },

        "project_type": {
            "label": "Type de projet",
            "data_type": "uuid",
            "required": False,
            "catalog": "PROJECT_TYPE",
        },

        "contract_reference": {
            "label": "Référence contractuelle",
            "data_type": "string",
            "required": False,
            "max_length": PROJECT_CONTRACT_REFERENCE_LENGTH,
        },

        "comments": {
            "label": "Commentaires",
            "data_type": "text",
            "required": False,
            "max_length": PROJECT_COMMENT_LENGTH,
        },

        # ------------------------------------------------------------------
        # Localisation
        # ------------------------------------------------------------------

        "address_1": {
            "label": "Adresse",
            "data_type": "string",
            "required": False,
            "max_length": PROJECT_ADDRESS_LENGTH,
        },

        "address_2": {
            "label": "Complément d’adresse",
            "data_type": "string",
            "required": False,
            "max_length": PROJECT_ADDRESS_LENGTH,
        },

        "address_3": {
            "label": "Complément d’adresse 2",
            "data_type": "string",
            "required": False,
            "max_length": PROJECT_ADDRESS_LENGTH,
        },

        "postal_code": {
            "label": "Code postal",
            "data_type": "postal_code",
            "required": False,
            "max_length": PROJECT_POSTAL_CODE_LENGTH,
        },

        "city": {
            "label": "Ville",
            "data_type": "string",
            "required": False,
            "max_length": PROJECT_CITY_LENGTH,
        },

        "country": {
            "label": "Pays",
            "data_type": "country",
            "required": False,
            "max_length": PROJECT_COUNTRY_LENGTH,
        },

        # ------------------------------------------------------------------
        # Charge et planning
        # ------------------------------------------------------------------

        "planned_workload_hours": {
            "label": "Charge prévisionnelle (h)",
            "data_type": "integer",
            "required": True,
            "default": PROJECT_DEFAULT_WORKLOAD_HOURS,
        },

        "contractual_start_date": {
            "label": "Date contractuelle de début",
            "data_type": "date",
            "required": False,
        },

        "contractual_end_date": {
            "label": "Date contractuelle de fin",
            "data_type": "date",
            "required": False,
        },

        "start_date_review": {
            "label": "Date révisée de début",
            "data_type": "date",
            "required": False,
        },

        "end_date_review": {
            "label": "Date révisée de fin",
            "data_type": "date",
            "required": False,
        },

        "receipt_date_init": {
            "label": "Date initiale de réception",
            "data_type": "date",
            "required": False,
        },

        "receipt_date_review": {
            "label": "Date révisée de réception",
            "data_type": "date",
            "required": False,
        },

        "delivery_date_init": {
            "label": "Date initiale de livraison",
            "data_type": "date",
            "required": False,
        },

        "delivery_date_review": {
            "label": "Date révisée de livraison",
            "data_type": "date",
            "required": False,
        },

        "effective_start_date": {
            "label": "Début",
            "data_type": "date",
            "required": False,
            "generated": True,
        },

        "effective_end_date": {
            "label": "Fin",
            "data_type": "date",
            "required": False,
            "generated": True,
        },
        
        "effective_receipt_date": {
            "label": "Réception",
            "data_type": "date",
            "required": False,
            "generated": True,
        },

        "effective_delivery_date": {
            "label": "Livraison",
            "data_type": "date",
            "required": False,
            "generated": True,
        },

        # ------------------------------------------------------------------
        # Données commerciales partageables
        # ------------------------------------------------------------------

        "amount_quote_ht": {
            "label": "Montant du devis HT",
            "data_type": "decimal",
            "required": True,
            "max_digits": PROJECT_AMOUNT_MAX_DIGITS,
            "decimal_places": PROJECT_AMOUNT_DECIMAL_PLACES,
            "default": PROJECT_DEFAULT_AMOUNT,
        },

        "amount_quote_ttc": {
            "label": "Montant du devis TTC",
            "data_type": "decimal",
            "required": True,
            "max_digits": PROJECT_AMOUNT_MAX_DIGITS,
            "decimal_places": PROJECT_AMOUNT_DECIMAL_PLACES,
            "default": PROJECT_DEFAULT_AMOUNT,
        },

        "amount_order_ht": {
            "label": "Montant de la commande HT",
            "data_type": "decimal",
            "required": True,
            "max_digits": PROJECT_AMOUNT_MAX_DIGITS,
            "decimal_places": PROJECT_AMOUNT_DECIMAL_PLACES,
            "default": PROJECT_DEFAULT_AMOUNT,
        },

        "amount_order_ttc": {
            "label": "Montant de la commande TTC",
            "data_type": "decimal",
            "required": True,
            "max_digits": PROJECT_AMOUNT_MAX_DIGITS,
            "decimal_places": PROJECT_AMOUNT_DECIMAL_PLACES,
            "default": PROJECT_DEFAULT_AMOUNT,
        },

        "currency": {
            "label": "Devise",
            "data_type": "currency",
            "required": True,
            "max_length": PROJECT_CURRENCY_LENGTH,
            "default": PROJECT_DEFAULT_CURRENCY,
        },

        "budget_comments": {
            "label": "Commentaires budgétaires",
            "data_type": "text",
            "required": False,
            "max_length": PROJECT_COMMENT_LENGTH,
        },

        # ------------------------------------------------------------------
        # Traçabilité
        # ------------------------------------------------------------------

        "created_at": {
            "label": "Date de création",
            "data_type": "datetime",
            "required": True,
            "generated": True,
        },

        "updated_at": {
            "label": "Dernière modification",
            "data_type": "datetime",
            "required": True,
            "generated": True,
        },
    },
}