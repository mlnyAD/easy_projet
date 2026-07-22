

# ADR-003 - Composant EPForm

## Statut

Accepté

## Date

2026-07-18

## Contexte

Toutes les applications possèdent des formulaires.

Sans composant commun, chaque écran devrait gérer :

- le rendu des champs ;
- les messages d'erreur ;
- les styles Tailwind ;
- les composants Preline.

Cela entraînerait une duplication importante.

## Décision

Créer un composant générique EPForm.

Le composant est indépendant du métier.

Il fournit :

- le rendu homogène des champs ;
- l'affichage des erreurs ;
- l'intégration Tailwind / Preline ;
- une présentation uniforme dans toute l'application.

Chaque application fournit uniquement son formulaire Django.

## Conséquences

Les formulaires métier deviennent beaucoup plus simples.

Toute évolution graphique est réalisée dans un seul composant.

L'interface reste cohérente dans l'ensemble de l'application.