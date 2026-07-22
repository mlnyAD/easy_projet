
1. Présentation

Easy Projet est une application de gestion de projets destinée aux PME du secteur du BTP.
Son architecture est conçue pour être modulaire, évolutive et facilement maintenable afin d'accompagner l'évolution fonctionnelle du produit sur le long terme.
Le présent document décrit l'organisation générale du projet. Il constitue le point d'entrée de la documentation d'architecture et permet de comprendre rapidement le rôle des principaux répertoires, des composants structurants et des conventions d'organisation.
Les sujets détaillés sont volontairement traités dans des documents spécialisés auxquels il est fait référence tout au long de ce guide.

À retenir : ce document présente l'organisation du projet. Il ne décrit pas le fonctionnement détaillé des composants.

Plus de détails dans :
- docs/philosophy.md
- docs/vision/principles.md

3. Vue d'ensemble du projet

Easy Projet est organisé autour de quatre ensembles complémentaires :
- la configuration de l'application ;
- les applications métier ;
- le socle commun de composants réutilisables ;
- la documentation technique et fonctionnelle.

Cette organisation permet de séparer clairement les responsabilités, de limiter les dépendances entre les modules et de faciliter l'évolution de l'application.

Figure – Vue d'ensemble de l'architecture
                               Easy Projet
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
 Configuration                 Applications               Documentation
      (config)                  métier (apps)                 (docs)
        │                            │
        │                            │
        │                ┌───────────┴────────────┐
        │                │                        │
        │          Domaine métier          Socle commun
        │             (apps)                (common)
        │                │                        │
        │                │                        │
        │        Companies, Projects...   Forms, UI, Models...
        │                │                        │
        └────────────────┴───────────────┬────────┘
                                         │
                                   Templates / Static
                                         │
                                    Utilisateur
Ensemble		Responsabilité
config			Configure l'application Django.
apps			Regroupe les domaines métier de l'application.
common			Fournit les composants techniques partagés.
templates		Assure la présentation de l'application.
static			Contient les ressources CSS, JavaScript et autres fichiers statiques.
docs			Centralise la documentation du projet.

À retenir :
L'architecture repose sur une séparation claire entre la configuration, le métier, les composants partagés et la présentation.

Voir aussi :
- docs/architecture/architecture_principles.md
- docs/ui/component_library.md

4. La racine du projet

La racine du projet regroupe les principaux répertoires et fichiers nécessaires au fonctionnement, au développement et à la maintenance d'Easy Projet.

Chaque élément possède une responsabilité clairement identifiée afin de faciliter l'organisation du code et son évolution.

Figure – Organisation de la racine du projet
easy_projet/
│
├── apps/          Applications métier
├── common/        Socle commun
├── config/        Configuration Django
├── docs/          Documentation
├── static/        Ressources statiques
├── templates/     Templates HTML
│
├── manage.py      Point d'entrée Django
├── README.md      Présentation du projet
└── CHANGELOG.md   Historique des évolutions

Élément		Rôle
apps		Contient les applications métier.
common		Regroupe les composants réutilisables.
config		Configure l'application Django.
templates	Contient les gabarits HTML.
static		Contient les ressources CSS, JavaScript, images…
docs		Regroupe la documentation du projet.
manage.py	Point d'entrée des commandes Django.
README.md	Présentation générale du projet.
CHANGELOG.md	Historique des versions et évolutions.

À retenir :
La racine du projet permet d'identifier rapidement les grands domaines qui composent l'application.

Voir aussi
- docs/architecture/architecture_principles.md

5. Configuration Django

La configuration de l'application est regroupée dans le répertoire config.
Elle centralise les paramètres nécessaires au fonctionnement du projet tout en les séparant du code métier.

Figure – Organisation de la configuration
config/
│
├── __init__.py
├── settings.py
├── urls.py
├── asgi.py
└── wsgi.py

Fichier		Rôle
settings.py	Paramètres de configuration de l'application.
urls.py		Déclaration des routes principales.
asgi.py		Point d'entrée ASGI.
wsgi.py		Point d'entrée WSGI.

À retenir :
Le répertoire config contient exclusivement les éléments de configuration de Django. Aucun code métier n'y est développé.

Voir aussi :
- docs/architecture/architecture_principles.md
- docs/development/development_guidelines.md

6. Les applications métier

7. Le socle commun (common)

8. Les templates

9. Les ressources statiques

10. La documentation

11. Ajouter une nouvelle fonctionnalité

12. Ajouter un nouveau composant

13. Conventions de nommage

14. Architecture cible