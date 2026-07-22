

# Philosophie de développement

## Pragmatisme

Le pragmatisme prime sur le formalisme.

Une règle est un guide de développement.
Elle ne doit jamais conduire à une solution plus complexe que le problème à résoudre.

## Simplicité

Toujours rechercher la solution la plus simple répondant correctement au besoin.

Éviter les abstractions prématurées.

## Métier

Le métier pilote l'architecture.

Les composants techniques sont au service du métier.

## Généralisation

On développe d'abord un cas métier concret.

Lorsque plusieurs cas présentent les mêmes besoins, on extrait un composant commun.

Ne jamais créer un composant générique uniquement parce qu'il pourrait être utile un jour.

## Composants

Chaque composant possède une responsabilité unique.

Les composants génériques ne contiennent aucune logique métier.

Le métier fournit les configurations.

Le composant fournit le comportement.

## Évolution

Toute architecture doit pouvoir évoluer sans remettre en cause les développements existants.