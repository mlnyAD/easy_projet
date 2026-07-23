

# 3. Composants du Framework

## 3.1 Objet

Le framework Easy Projet constitue le socle technique commun de l'application.

Il fournit un ensemble de composants génériques permettant de développer les différents domaines fonctionnels de manière homogène, cohérente et réutilisable.

Le framework ne contient aucune logique métier propre aux applications. Son rôle est exclusivement de fournir les mécanismes communs nécessaires au développement.

Les composants du framework sont conçus pour être indépendants des domaines fonctionnels et réutilisables dans l'ensemble du projet.

---

# 3.2 Principes généraux

Le framework repose sur les principes suivants :

- responsabilité unique des composants ;
- séparation stricte des couches techniques ;
- forte réutilisabilité ;
- absence de duplication de code ;
- composants indépendants des domaines métier ;
- architecture orientée services.

Chaque composant possède une responsabilité clairement identifiée et ne doit jamais empiéter sur celle d'un autre composant.

---

# 3.3 Bootstrap

## 3.3.1 Objet

Le bootstrap permet d'initialiser les données techniques et les données de référence nécessaires au fonctionnement de l'application.

Il constitue le mécanisme officiel de chargement des référentiels Easy Projet.

Les données chargées par bootstrap sont notamment :

- catalogues de référence ;
- paramètres système ;
- données techniques communes ;
- futurs référentiels du framework.

---

## 3.3.2 Architecture

Chaque domaine fonctionnel peut disposer de son propre bootstrap.

Le framework centralise leur exécution au travers d'un registre unique.

Chaque bootstrap est autonome et responsable du chargement de son propre domaine.

---

## 3.3.3 Enregistrement

Chaque bootstrap est enregistré auprès du registre du framework.

Le framework découvre automatiquement les bootstraps enregistrés puis les exécute.

Aucun bootstrap ne doit être exécuté directement par un domaine fonctionnel.

---

## 3.3.4 Dépendances

Un bootstrap peut déclarer des dépendances vis-à-vis d'autres bootstraps.

Le framework garantit alors l'ordre d'exécution.

Cette approche permet de conserver une architecture modulaire tout en assurant la cohérence des données chargées.

---

## 3.3.5 Cycle d'exécution

Le cycle d'exécution d'un bootstrap est le suivant :

1. découverte des bootstraps enregistrés ;
2. résolution des dépendances ;
3. exécution des bootstraps dans l'ordre déterminé ;
4. validation de l'exécution.

Chaque bootstrap est indépendant et ne connaît pas les mécanismes internes des autres bootstraps.

---

## 3.3.6 Idempotence

Un bootstrap doit obligatoirement être **idempotent**.

Son exécution peut être répétée autant de fois que nécessaire sans :

- créer de doublons ;
- supprimer des données existantes ;
- modifier inutilement les données déjà présentes.

Cette propriété garantit la reproductibilité des installations ainsi que la fiabilité des mises à jour.

---

## 3.3.7 Règles d'implémentation

Un bootstrap :

- orchestre le chargement des données ;
- utilise exclusivement les services du domaine ;
- ne contient aucune règle métier ;
- n'accède jamais directement aux modèles Django.

Le bootstrap constitue une couche d'orchestration et non une couche métier.

---

# 3.4 Définitions métier

## 3.4.1 Objet

Les données techniques du framework sont décrites au moyen de définitions Python.

Ces définitions constituent la source officielle des référentiels de l'application.

---

## 3.4.2 Dataclasses

Les définitions utilisent des dataclasses représentant les objets métier.

Exemples :

- CatalogDefinition
- CatalogValueDefinition
- EntityDefinition

Ces objets décrivent les données indépendamment de leur mode de persistance.

Ils constituent le point d'entrée des mécanismes de validation, de bootstrap et de persistance.

---

## 3.4.3 Alignement des couches

Une définition métier conserve la même structure fonctionnelle tout au long de son cycle de traitement.

Le flux est le suivant :

```
Définition métier
        │
        ▼
Bootstrap
        │
        ▼
Service métier
        │
        ▼
Modèle Django
        │
        ▼
Base PostgreSQL
```

Le bootstrap ne doit jamais effectuer d'adaptation fonctionnelle entre les couches.

Toute évolution de structure doit être réalisée au niveau des composants concernés et non dans le bootstrap.

---

## 3.4.4 Source officielle des données

Les définitions Python constituent la référence officielle des données techniques.

La base de données représente l'état courant de ces définitions.

Toute évolution d'un référentiel doit être réalisée dans les définitions avant d'être propagée en base via le bootstrap.

---

# 3.5 Composants génériques

Le framework est destiné à accueillir progressivement les composants génériques utilisés par l'ensemble des domaines fonctionnels.

Les composants actuellement prévus sont notamment :

- EPList
- EPForm
- EPDetail
- Workflow
- Bootstrap
- Dictionary
- Validation
- Reporting
- Notifications
- Sécurité

Chaque composant fait l'objet d'une documentation spécifique lors de sa validation.

---

# 3.6 Évolutions

Le framework Easy Projet est conçu pour évoluer progressivement.

Chaque nouveau composant générique devra respecter les principes définis dans le présent document :

- indépendance vis-à-vis des domaines métier ;
- responsabilité unique ;
- réutilisabilité ;
- faible couplage ;
- documentation systématique.

Les composants ne sont intégrés au framework qu'après validation fonctionnelle, technique et documentaire.

---

# 3.7 Conclusion

Le framework constitue le socle technique d'Easy Projet.

Il garantit une architecture homogène, une forte réutilisabilité des composants et une évolution maîtrisée de l'application.

Toute évolution du framework doit préserver ces principes afin de maintenir la cohérence globale du projet.