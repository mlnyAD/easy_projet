

# 04 - Architecture d'EPForm

## Objectif

EPForm est le composant générique du framework Easy Projet permettant de décrire un formulaire métier de manière entièrement déclarative.

Les applications métier ne décrivent jamais le rendu graphique.

Elles décrivent uniquement les informations fonctionnelles.

Le framework est responsable de la transformation en interface utilisateur.

---

## Architecture

FieldDefinition
        │
        ▼
ResolvedField
        │
        ├── définition métier
        └── BoundField Django
        │
        ▼
Template tags
        │
        ▼
Design System
        │
        ▼
Templates

---

## Responsabilités

### Application métier

Décrit :

- le nom
- le type
- le libellé
- les règles métier
- le provider
- la visibilité

Elle ne décrit jamais :

- Tailwind
- HTML
- classes CSS
- widgets Django

---

### Framework

Le framework transforme la définition métier en modèle exploitable.

Il construit :

- ResolvedField
- ResolvedSection
- EPForm

---

### Intégration Django

Elle associe :

FieldDefinition

avec

BoundField

afin d'obtenir un ResolvedField.

---

### Design System

Le Design System choisit :

- les composants graphiques
- les classes CSS
- les attributs ARIA
- les icônes
- les couleurs
- les états

Aucune logique métier.

---

### Templates

Les templates n'effectuent aucun traitement.

Ils affichent uniquement les composants fournis.

---

## Principe

Le métier décrit :

"ce qu'il faut afficher"

Le framework décide :

"comment l'afficher"

---

## Évolutivité

Un nouveau widget ne nécessite jamais de modifier une application métier.

Seuls le Design System et les template tags évoluent.

Les définitions métier restent compatibles.