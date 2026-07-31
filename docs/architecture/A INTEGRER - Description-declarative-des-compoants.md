

03 - Principe de description déclarative des composants
Objectif

Le framework Easy Projet est basé sur une architecture déclarative.

Le développeur décrit ce qu'il souhaite obtenir ; le framework est responsable de déterminer comment le produire.

Les applications métier ne doivent contenir aucune logique de présentation.

Principe général

Une application métier décrit un composant à l'aide d'une définition.

Exemple :

ColumnDefinition(
    identifier="company_name",
    label="Société",
    width="lg",
    align="left",
    truncate=True,
    sortable=True,
)

Cette définition constitue le contrat entre l'application métier et le framework.

Responsabilités
Application métier

L'application métier décrit :

les données ;
les comportements souhaités ;
les caractéristiques d'affichage.

Elle ne décrit jamais :

les classes CSS ;
les templates ;
le HTML ;
Tailwind.
Framework

Le framework transforme cette description en un modèle d'affichage.

Il :

valide les définitions ;
construit les ViewModels ;
prépare les données destinées au rendu.
Intégration Django

L'intégration Django traduit le ViewModel vers la technologie utilisée.

Elle :

associe les propriétés sémantiques aux classes CSS ;
prépare le contexte des templates ;
produit le HTML final.
Design System

Le Design System définit l'apparence graphique.

Il centralise :

les classes CSS ;
les variantes graphiques ;
les couleurs ;
les espacements ;
les composants visuels.

Aucune règle métier ne doit apparaître dans cette couche.

Chaîne de transformation
Définition métier
        │
        ▼
Framework
        │
        ▼
ViewModel
        │
        ▼
Intégration Django
        │
        ▼
Design System
        │
        ▼
Templates
        │
        ▼
HTML

Chaque niveau possède une responsabilité unique.

Conséquences

L'ajout d'une nouvelle propriété consiste uniquement à :

enrichir la définition ;
la valider ;
l'exposer dans le ViewModel ;
définir son rendu dans l'intégration Django.

Les templates restent inchangés ou n'évoluent que très peu.

Exemple

L'ajout de l'alignement des colonnes n'a nécessité que :

l'ajout de align dans ColumnDefinition ;
la validation de cette propriété ;
son exposition dans ViewColumn ;
une table de correspondance CSS ;
un filtre Django.

Aucune logique métier n'a été ajoutée dans les templates.