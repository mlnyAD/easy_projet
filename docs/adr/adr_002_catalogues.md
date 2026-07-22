

# ADR-002 - Architecture des catalogues

## Statut

Accepté

## Date

2026-07-18

## Contexte

L'application utilise de nombreuses listes de valeurs.

Certaines sont fixes (états, types...).

D'autres doivent pouvoir être enrichies par les utilisateurs.

Il était nécessaire d'éviter la multiplication des petites tables de références.

## Décision

Tous les catalogues reposent sur deux tables génériques :

- CatalogType
- CatalogValue

Chaque catalogue est décrit par son type.

Les valeurs appartiennent à un type.

Les catalogues peuvent être :

- fixes ;
- hiérarchiques ;
- incrémentaux.

Les catalogues sont globaux à l'application et non spécifiques à une société.

## Conséquences

Cette architecture :

- réduit fortement le nombre de tables ;
- simplifie la maintenance ;
- facilite l'ajout de nouveaux catalogues ;
- offre un comportement homogène dans toute l'application.