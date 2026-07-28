

# 1 Objet

Le présent document définit le langage de description des entités métier utilisé par le Framework Easy Projet.

Il constitue la référence permettant de décrire de manière déclarative les entités, leurs propriétés et leur présentation.

Le dictionnaire métier ne décrit jamais les traitements. Il décrit exclusivement la structure fonctionnelle des données.

# 2 Principes 

Le dictionnaire métier constitue la source unique de vérité décrivant une entité métier. Les autres composants du framework (EntityDefinition, FormDefinition, ListDefinition, ViewModel, etc.) sont construits à partir de cette description et ne doivent pas dupliquer ces informations.

Un dictionnaire métier est autoporteur. Sa lecture doit permettre de comprendre l'entité sans dépendre d'autres définitions métier. La mutualisation est réservée aux composants techniques du framework.

Quelques règles simples, par exemple :

- un dictionnaire décrit le métier ;
- le framework décrit le comportement ;
- un dictionnaire ne contient aucune logique métier ;
- une propriété possède une seule signification ;
- toute propriété est réutilisable par toutes les entités ;
- un dictionnaire est déclaratif ;
- un dictionnaire est indépendant de la persistance ;
- un dictionnaire est indépendant de l'interface utilisateur ;
- une propriété possède une définition unique dans tout le produit ;
- une propriété est documentée avant d'être utilisée ;
- le dictionnaire constitue le contrat entre le métier et le framework.

# 3 Structure générale

        Dictionary
            │
            ▼
        DictionaryValidator
            │
            ▼
      Entity Definition
        │
        ├── Métadonnées
        │
        ├── Fields
        │       │
        │       ├── data
        │       ├── list
        │       ├── form
        │       └── detail
        │
        └── Validation

# 4 Définition d'une entité

Métadonnées obligatoires
    name
    label
    plural
Métadonnées optionnelles
    category
    description
    icon
    order
    permissions
    help
    tags

# 5 Définition des champ

Les sections autorisées :

- data
- list
- form
- detail
...

Les sections constituent les différents contextes dans lesquels une propriété peut être utilisée.

# 6 Définition des sections

Pour chaque section :

- objectif ;
- comportement ;
- propriétés autorisées ;
- propriétés interdites ;
- valeurs par défaut ;
- exemples.

Pour chaque propriété :

    Nom
    Description
    Type
    Valeurs autorisées
    Valeur par défaut
    Obligatoire
    Sections autorisées
    Entités concernées
    Exemple
    Remarques

Il faut classer les propriétés.
Par exemple :

Métadonnées
- name
- label
- description
- plural
- icon
Validation
- required
- readonly
- nullable
- unique
Affichage
- visible
- width
- align
- sortable
Recherche
- searchable
- filterable
- indexed
Édition
- editable
- placeholder
- help_text
Référencement
- catalog
- relation
- display_field

Cette classification facilitera énormément la maintenance.

Ainsi toutes les propriétés seront documentées de la même manière.

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
- la stabilité des noms une fois publiés ;
- les codes techniques ne sont jamais traduits ;
- les libellés utilisateur peuvent être localisés ;
- les noms publiés sont considérés comme des contrats de compatibilité.

# 9 Règles d'évolution

Une propriété ne peut être ajoutée que si :

- elle est générique ;
- elle concerne plusieurs entités ;
- elle n'introduit pas de logique métier;
- elle ne duplique pas une propriété existante ;
- sa documentation est complète ;
- son impact sur la compatibilité est maîtrisé.

# 10 Entités de référence

# 11 Cycle de vie d'une entité

Dictionnaire métier
        │
        ▼
Validation
        │
        ▼
EntityDefinition
        │
        ├── FormDefinition
        ├── ListDefinition
        ├── Providers
        ├── ViewModels
        └── Documentation


        ---> à intégrer

        Règle : Dictionnaire métier autoporteur
Principe

Le dictionnaire métier constitue la description complète d'une entité métier.

Sa lecture doit permettre de comprendre immédiatement :

la finalité de l'entité ;
les propriétés qu'elle expose ;
la signification de chaque propriété.

La compréhension d'une entité ne doit pas nécessiter la consultation d'autres dictionnaires métier.

Conséquences

Le dictionnaire contient :

les métadonnées de l'entité ;
la définition complète de chaque propriété ;
les caractéristiques fonctionnelles de ces propriétés.

Le dictionnaire ne contient pas :

de logique métier ;
de logique de présentation ;
de logique technique ;
de logique de persistance.
Mutualisation

La mutualisation est réservée aux éléments techniques du framework :

constantes ;
validateurs ;
composants ;
moteurs de rendu ;
providers ;
services ;
utilitaires.

Les définitions métier restent locales à chaque dictionnaire afin de préserver leur lisibilité et leur autonomie.

Je pense également que nous avons progressivement fait émerger une hiérarchie très claire des responsabilités :

                Framework
                    │
        ┌───────────┼───────────┐
        │           │           │
 Validation     Rendu UI    Providers
        │           │           │
        └───────────┼───────────┘
                    │
            Dictionnaire métier
                    │
             Entité fonctionnelle
                    │
             Modèle de persistance