

# 1. Objet

Le présent document décrit les principes de persistance des données au sein d'Easy Projet.

La persistance garantit la conservation, l'intégrité et la disponibilité des informations manipulées par les applications du produit. 

# 2 Rôle de la persistance
Elle garantit :

- la conservation des données métier ;
- l'intégrité des informations ;
- l'isolation des environnements ;
- la traçabilité des opérations ;
- la disponibilité des données ;
- la conservation des historiques ;
- la cohérence entre les différentes représentations d'une même information.

# 3 Principes de conception

- stockage durable des données ;
- séparation des données métier, documentaires et techniques ;
- isolation stricte des environnements ;
- conservation de l'historique ;
- absence de suppression physique lorsque la traçabilité doit être conservée ;
- intégrité référentielle ;
- évolutivité du modèle de données ;
- indépendance vis-à-vis des applications métier.

# 4 Organisation de la persistance

                   Persistance
                         │
        ┌────────────────┴─────────────────┐
        │                                  │
        ▼                                  ▼
 Environnement client             Informations globales
        │                                  │
        │                          Catalogues techniques
        │                          Paramètres système
        │                          Licences
        │
        ├─────────────────────────────────────────────────┐
        │                 │                │              │
        ▼                 ▼                ▼              ▼
 Données métier     Documents        Historique      Journalisation

 # 5 Modèle de propriété des données

Toute donnée appartient à un environnement client.

Les opérateurs créent ou modifient des données mais n'en deviennent jamais propriétaires.

Le changement d'affectation d'un opérateur n'entraîne aucun transfert de propriété.

Les historiques restent associés aux données afin de garantir la traçabilité complète des projets.

# 6 Règles d'utilisation

Les règles d'utilisation assurent que :

- toute donnée métier appartient à un environnement ;
- toute lecture est filtrée par l'environnement actif ;
- les suppressions physiques sont exceptionnelles ;
- les relations référentielles doivent être préservées ;
- les historiques ne doivent jamais être altérés ;
- les migrations doivent préserver les données existantes.

# 7 Évolutions

Les évolutions du modèle de persistance devront préserver :

- la compatibilité avec les principes d'architecture ;
- l'isolation des environnements ;
- la conservation des historiques ;
- la stabilité des identifiants ;
- la cohérence des données.