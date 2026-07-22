

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
      ┌────────────────────┼────────────────────┐
      │                    │                    │
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


# 3. Principes de découpage

L'architecture générale d'Easy Projet repose sur les principes définis dans le document 00-principes-architecture.md.

Les responsabilités sont réparties entre plusieurs composants spécialisés.

Chaque composant poursuit un objectif unique.

Les interactions entre composants sont limitées afin de conserver un faible couplage.

Les composants communiquent exclusivement par leurs interfaces publiques.

# 4. Les grandes briques logicielles

| Composant             | Responsabilité                                                        |
| --------------------- | --------------------------------------------------------------------- |
| Interface utilisateur | Présenter les informations et recueillir les actions des utilisateurs |
| Applications métier   | Mettre en œuvre les fonctions du produit                              |
| Composants génériques | Fournir des mécanismes communs réutilisables                          |
| Services transverses  | Mutualiser les services utilisés par plusieurs composants             |
| Persistance           | Conserver durablement les informations                                |
| Connecteurs externes  | Assurer les échanges avec les systèmes externes                       |

# 5. Les interactions entre les briques

                  Utilisateur
                       │
                       ▼
            Interface utilisateur
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
 Applications métier         Services transverses
          │                         │
          ├──────────────┐          │
          ▼              ▼          ▼
     Persistance   Connecteurs externes
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     OnlyOffice      Service IA      Microsoft 365
     
                      
# 6. Évolutions

L'architecture d'Easy Projet est conçue pour évoluer progressivement.

De nouveaux domaines métier, services transverses ou connecteurs externes pourront être ajoutés sans remettre en cause l'organisation générale du système.

Les évolutions devront respecter les principes d'architecture définis dans le document « 00-principes-architecture.md » afin de préserver la cohérence et la pérennité du produit.