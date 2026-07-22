

# ADR-004 – Composant EPList

## Statut

Accepté

## Contexte

Toutes les applications métiers possèdent des listes.

Ces listes présentent de nombreux comportements communs.

## Décision

La première implémentation est réalisée sur la liste des sociétés.

Le composant EPList sera extrait progressivement à partir de cette implémentation.

Aucune généralisation n'est réalisée avant validation sur un cas réel.

## Fonctionnalités prévues

- affichage
- pagination
- tri
- filtres
- sélection des colonnes
- mémorisation des préférences
- export
- actions de masse

## Principe

Le métier décrit les données.

EPList gère leur présentation.