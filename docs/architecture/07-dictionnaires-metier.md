

# 1 Objet

Définir le langage de description des entités métier utilisé par le Framework Easy Projet.

# 2 Principes 

Quelques règles simples, par exemple :

- un dictionnaire décrit le métier ;
- le framework décrit le comportement ;
- un dictionnaire ne contient aucune logique métier ;
- une propriété possède une seule signification ;
- toute propriété est réutilisable par toutes les entités.

# 3 Structure générale

Entity
    ↓
Fields
    ↓
Sections
    ↓
Propriétés

# 4 Définition d'une entité

Les propriétés autorisées :

name
label
plural
category
icon
description
...

# 5 Définition des champ

Les sections autorisées :

- data

- list

- form

- detail

...

Aucune autre.

# 6 Définition des sections

Pour chaque section :

- rôle ;
- propriétés autorisées ;
- valeurs par défaut.

# 7 Catalogue des propriétés

C'est probablement la partie la plus importante.

Par exemple :

- required
- Objet
- Type
- Valeur par défaut
- Utilisé par
- Exemple

Puis :

- readonly

Puis :

- searchable

etc.

Cette partie deviendra la documentation de référence du Framework.

# 8 Règles de nommage

les règles de nommage devront fixer:
- les noms d’entités au singulier ;
- les noms de champs en snake_case ;
- les noms techniques en anglais ;
- les libellés utilisateur en français ;
- les booléens préfixés par is_, has_, can_ ou allows_ selon leur sens ;
- les clés étrangères suffixées par _id uniquement au niveau de la persistance, pas nécessairement dans le dictionnaire métier ;
- les dates suffixées par _at pour les horodatages et _date pour les dates métier ;
- les constantes et dictionnaires racine en majuscules ;
- l’interdiction des abréviations ambiguës ;
- la stabilité des noms une fois publiés.

# 9 Règles d'évolution

Une propriété ne peut être ajoutée que si :

- elle est générique ;
- elle concerne plusieurs entités ;
- elle n'introduit pas de logique métier.

# 10 Exemple complet (Company)