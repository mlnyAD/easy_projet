

# Principes d'architecture Easy Projet

## Objet

Ce document présente les principes fondateurs de l'architecture d'Easy Projet.

Ces principes guident les choix de conception, les développements et les évolutions du produit.

Ils constituent les règles de référence du projet. Toute décision d'architecture doit être cohérente avec ces principes ou justifier explicitement une exception.

L'objectif est de construire un produit robuste, maintenable et évolutif, tout en conservant une architecture simple à comprendre.

## Champ d'application

Les principes définis dans ce document s'appliquent à l'ensemble du projet Easy Projet.

Ils concernent notamment :
- l'architecture générale de l'application ;
- le développement des composants génériques ;
- le développement des modules métier ;
- l'organisation de la base de données ;
- les interfaces utilisateur ;
- les tests ;
- la documentation technique et fonctionnelle.

Ces principes constituent le cadre de référence du projet.

Toute évolution importante doit être évaluée au regard de ces principes avant sa mise en œuvre.

Une exception peut être retenue lorsqu'elle apporte un bénéfice clairement identifié. Elle doit alors être explicitement documentée et justifiée.

## Principes fondateurs

1. Une seule source de vérité

Chaque information est définie une seule fois dans le système.

Toute duplication constitue une exception qui doit être justifiée.

2. Généricité maîtrisée

Les mécanismes communs sont mutualisés au sein de composants génériques.

La généricité ne doit jamais rendre le système plus complexe que nécessaire.

3. Simplicité avant sophistication

La solution la plus simple répondant correctement au besoin est privilégiée.

Une architecture simple est plus facile à comprendre, à maintenir et à faire évoluer.

4. Séparation des responsabilités

Chaque composant possède une responsabilité clairement identifiée.

Les couches fonctionnelles, techniques et de présentation restent indépendantes autant que possible.

5. Pérennité du produit

Les décisions d'architecture sont prises dans une perspective de long terme.

La facilité de maintenance, la stabilité et l'évolutivité priment sur les gains de développement à court terme.

6. L'identité est indépendante des autorisations

L'identité d'un opérateur est unique et pérenne.

Les droits d'accès ne dépendent jamais de son identité mais exclusivement de ses appartenances actives, de ses responsabilités et des autorisations qui lui sont accordées.

Une identité ne constitue jamais une permission.

7. Les environnements sont totalement isolés

Chaque environnement client constitue un espace de travail autonome.

Aucune donnée ne peut être consultée, modifiée ou recherchée en dehors de son environnement, sauf par les mécanismes explicitement prévus à cet effet.

L'isolation des environnements constitue un principe fondamental de sécurité.

8. Les données appartiennent à leur environnement

Les données produites dans Easy Projet appartiennent à l'environnement dans lequel elles ont été créées.

L'auteur d'une donnée en conserve la traçabilité mais n'en est jamais propriétaire.

Le changement d'affectation ou le départ d'un opérateur n'entraîne jamais le transfert de propriété des données.

9. La traçabilité est permanente

Les contributions des opérateurs sont conservées afin de garantir l'historique complet des projets.

La suppression d'un accès ou le départ d'un collaborateur ne doit jamais altérer l'historique des actions réalisées.

10. La mobilité des opérateurs est un fonctionnement normal

11. Séparation des vocabulaires

- Easy Projet distingue systématiquement le vocabulaire métier du vocabulaire technique.

- Les interfaces utilisateur, les messages, les aides et la documentation fonctionnelle utilisent exclusivement le vocabulaire métier.
- Les documents d'architecture et le code source utilisent le vocabulaire technique lorsque cela est nécessaire.
- Chaque concept métier possède une correspondance unique dans l'architecture technique, afin d'éviter toute ambiguïté.

L'architecture doit permettre à un opérateur de rejoindre, quitter ou réintégrer un environnement sans compromettre la sécurité ni la cohérence des données.

Les changements d'organisation des entreprises constituent un cas nominal de fonctionnement et non une exception.

## Invariants architecturaux

Les principes définis dans ce document constituent les invariants de l'architecture d'Easy Projet.

Toute évolution fonctionnelle, technique ou organisationnelle doit pouvoir être mise en œuvre sans remettre en cause ces invariants.

Lorsqu'une évolution semble nécessiter leur remise en cause, une révision de l'architecture doit être engagée avant tout développement.

## Règles d'application

Les principes fondateurs définissent les objectifs de l'architecture.

Les règles d'application précisent la manière de les mettre en œuvre au quotidien.

### 1. Concevoir avant de développer

Toute évolution importante fait l'objet d'une réflexion préalable.

L'architecture est définie avant l'écriture du code.

---

### 2. Documenter les décisions

Toute décision ayant un impact significatif sur l'architecture est documentée.

Les décisions majeures sont formalisées dans une Architecture Decision Record (ADR).

---

### 3. Développer des composants réutilisables

Lorsqu'un mécanisme est utilisé par plusieurs modules, il doit être étudié afin de déterminer s'il peut être mutualisé dans un composant générique.

La généricité ne doit jamais être recherchée au détriment de la simplicité.

---

### 4. Séparer les responsabilités

Chaque composant possède une responsabilité clairement identifiée.

Les règles métier, les composants techniques et les interfaces utilisateur doivent rester indépendants autant que possible.

---

### 5. Éviter les duplications

Une information ne doit être définie qu'une seule fois.

Les duplications ne sont acceptées que lorsqu'elles sont justifiées par des contraintes techniques ou de performance.

---

### 6. Développer de manière incrémentale

Chaque sujet est traité jusqu'à son aboutissement avant d'entreprendre un nouveau chantier.

Cette approche favorise la qualité, facilite les tests et limite les régressions.

---

### 7. Garantir la cohérence du projet

Toute nouvelle fonctionnalité doit respecter les principes définis dans le présent document.

En cas de doute, la solution retenue est celle qui préserve le mieux la cohérence globale du produit.

	
## Conclusion

Les principes définis dans ce document constituent le cadre de référence de l'architecture d'Easy Projet.

Ils ont pour objectif de garantir la cohérence, la qualité, la maintenabilité et la pérennité de l'application tout au long de son évolution.

Ils s'appliquent à l'ensemble des développements, qu'ils concernent les composants techniques, les modules métier, les interfaces utilisateur ou la documentation.

Toute décision d'architecture doit être prise en conformité avec ces principes. Lorsqu'une exception est nécessaire, elle doit être explicitement motivée et documentée afin de préserver la compréhension et la cohérence globale du projet.

Ce document est destiné à évoluer avec le projet. Il constitue le socle sur lequel reposent les choix techniques et méthodologiques d'Easy Projet.