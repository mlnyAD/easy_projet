

# 1. Objet

Ce document présente l'architecture générale d'Easy Projet.

Il décrit les principaux composants logiciels du système, leurs responsabilités respectives et leurs interactions.

Il constitue le point d'entrée de la documentation d'architecture et sert de référence pour les documents décrivant plus en détail chacun des composants.

# 2. Vue d'ensemble

Easy Projet est organisé en un ensemble de composants logiciels spécialisés.

Chaque composant possède une responsabilité clairement identifiée et collabore avec les autres composants afin de répondre aux besoins décrits dans le cahier des charges fonctionnel.

Cette séparation permet :

- une évolution indépendante des composants ;
- une maintenance facilitée ;
- une meilleure réutilisation ;
- une architecture pérenne.

                     Easy Projet
                           │
                           ▼
              Environnement client actif
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
Interface          Applications         Services
utilisateur            métier          transverses
                           │
              ┌────────────┼─────────────┐
              ▼                          ▼
     Composants génériques     Connecteurs externes
              │                          │
              └────────────┬─────────────┘
                           ▼
                     Persistance

Easy Projet est une application SaaS multi-environnement. Chaque environnement client constitue un espace de travail totalement isolé des autres. L'ensemble des composants applicatifs fonctionne dans le contexte d'un environnement actif, garantissant l'isolation des données et des traitements.

Les principes d'isolation des environnements et le modèle multi-environnement sont détaillés dans les documents 08 – Environnement client et isolation des données et 09 – Modèle de données multi-tenant.

# 3. Principes de découpage

L'architecture générale d'Easy Projet repose sur les principes définis dans le document 00-principes-architecture.md.

Les responsabilités sont réparties entre plusieurs composants spécialisés.

Chaque composant poursuit un objectif unique.

Les interactions entre composants sont limitées afin de conserver un faible couplage.

Les composants communiquent exclusivement par leurs interfaces publiques.

Tous les composants applicatifs sont indépendants des mécanismes d'authentification et d'identité. Ils manipulent les données uniquement dans le contexte de l'environnement actif et des autorisations calculées pour l'opérateur courant.

# 4. Les grandes briques logicielles

| Composant                  | Responsabilité                                                        |
| -------------------------- | --------------------------------------------------------------------- |
| Gestion des environnements | Déterminer le contexte de travail, assurer l'isolation des            |
|                            | données et appliquer les règles d'accès.                              |
| Interface utilisateur      | Présenter les informations et recueillir les actions des utilisateurs |
| Applications métier        | Mettre en œuvre les fonctions du produit                              |
| Composants génériques      | Fournir des mécanismes communs réutilisables                          |
| Services transverses       | Mutualiser les services utilisés par plusieurs composants             |
| Persistance                | Conserver durablement les informations                                |
| Connecteurs externes       | Assurer les échanges avec les systèmes externes                       |

# 5. Les interactions entre les briques

                                   Utilisateur
                      │
                      ▼
             Authentification
                      │
                      ▼
      Résolution de l'environnement actif
                      │
                      ▼
          Interface utilisateur
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
Applications métier        Services transverses
         │                         │
         ├──────────────┐          │
         ▼              ▼          ▼
    Persistance   Connecteurs externes
     
                      
# 6. Évolutions

L'architecture d'Easy Projet est conçue pour évoluer progressivement.

De nouveaux domaines métier, services transverses ou connecteurs externes pourront être ajoutés sans remettre en cause l'organisation générale du système.

Les évolutions devront respecter les principes d'architecture définis dans le document « 00-principes-architecture.md » afin de préserver la cohérence et la pérennité du produit.

En particulier, aucune évolution ne devra remettre en cause :

- l'isolation des environnements ;
- la séparation entre identité et autorisations ;
- la propriété des données par leur environnement ;
- la conservation de la traçabilité ;
- les principes fondateurs définis dans le document 00 – Principes d'architecture.