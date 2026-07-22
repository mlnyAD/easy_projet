

# ADR-005 — Dictionnaire métier

## Statut

Adoptée

## Contexte

Le Framework doit décrire le métier sans dépendre d'une technologie particulière.

## Décision

Le dictionnaire métier :

- décrit uniquement le métier ;
- ne contient aucune propriété spécifique à Django ;
- constitue la source unique de vérité des métadonnées.

## Conséquences

- les adaptateurs traduisent vers Django ;
- une modification est effectuée en un seul endroit ;
- le Framework devient indépendant de la technologie.