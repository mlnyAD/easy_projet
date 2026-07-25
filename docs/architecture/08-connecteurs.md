

# 1 Objet

Le présent document définit les règles permettant d'échanger avec des services ou applications tiers tout en garantissant l'indépendance et la pérennité de l'architecture.
Easy Projet dépend de contrats d'échange, jamais de produits ou de fournisseurs.
Les connecteurs externes constituent la seule couche autorisée à communiquer avec des systèmes tiers. Ils assurent l'indépendance de la plateforme vis-à-vis des fournisseurs et préservent la stabilité de l'architecture.

# 2 Rôle des connecteurs externes

Les connecteurs externes assurent les échanges entre Easy Projet et les systèmes tiers.

Ils sont responsables de :

- traduire les demandes internes vers le protocole attendu par le système externe ;
- recevoir et interpréter les réponses ;
- isoler les spécificités techniques des fournisseurs ;
- garantir la stabilité des échanges,
- garantir que les échanges respectent le contexte de l'environnement actif lorsque les données manipulées sont propres à un environnement client.

Les applications métier ne communiquent jamais directement avec un système externe.

# 3 Principes de conception

Les connecteurs externes reposent sur les principes suivants :

- les applications métier dépendent de contrats d'échange et non de fournisseurs ;
- chaque technologie externe est isolée dans un composant dédié ;
- les interfaces de communication sont stables, documentées et, lorsque cela est possible, fondées sur des protocoles normalisés ;
- un fournisseur peut être remplacé sans modifier les applications métier ;
- les échanges doivent être sécurisés, traçables et maîtrisés ;
- les contraintes techniques, contractuelles ou organisationnelles imposées par un client doivent pouvoir être prises en compte sans remettre en cause l'architecture globale,
- les connecteurs ne portent aucune règle métier ;
- les connecteurs ne contournent jamais les mécanismes de sécurité et d'autorisation du produit.

# 4 Organisation des connecteurs

Les connecteurs sont organisés par capacité fonctionnelle et non par produit.

                    Easy Projet
                          │
                 Environnement actif
                          │
                 Services transverses
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    Édition         Intelligence      Visualisation
 documentaire       artificielle          CAO
          │               │               │
          ▼               ▼               ▼
     Adaptateur      Adaptateur      Adaptateur
          │               │               │
          ▼               ▼               ▼
     Fournisseur     Fournisseur     Fournisseur

| Capacité                  | Exemples d'implémentation                     |
| ------------------------- | --------------------------------------------- |
| Édition documentaire      | OnlyOffice, Microsoft 365, Collabora…         |
| Intelligence artificielle | IA interne, OpenAI, Mistral, Anthropic…       |
| Visualisation CAO         | CADViewer ou toute solution équivalente       |
| Cartographie              | OpenStreetMap, IGN, Google Maps…              |
| Messagerie                | Serveur SMTP de l'entreprise ou service tiers |
| Stockage documentaire     | Système interne, stockage objet, GED…         |
| Authentification fédérée  | Active Directory, Microsoft Entra ID, LDAP,   |
|                           | OpenID Connect...                             |

Les implémentations citées sont données à titre d'exemple. Elles ne constituent pas des choix d'architecture.

# 5 Règles d'utilisation

Les règles suivantes s'appliquent à l'ensemble des connecteurs :

- toute communication avec un système externe passe par un connecteur dédié ;
- un connecteur ne traite que les échanges avec le système qu'il représente ;
- les applications métier ignorent la technologie utilisée par le fournisseur ;
- les protocoles de communication doivent être documentés et respectés ;
- les erreurs et indisponibilités des systèmes externes doivent être maîtrisées sans compromettre la stabilité d'Easy Projet ;
- toute évolution ou remplacement d'un fournisseur doit être limité au connecteur concerné ;
- les connecteurs ne stockent pas d'information métier durable ;
- les connecteurs ne modifient jamais les règles métier 
- les connecteurs propagent le contexte d'exécution lorsque celui-ci est nécessaire aux systèmes tiers ;
- les erreurs d'un fournisseur ne doivent jamais compromettre la cohérence des données d'Easy Projet.

# 6 Évolutions

L'architecture des connecteurs est conçue pour intégrer de nouveaux services ou remplacer des fournisseurs existants sans modifier les applications métier.

Les connecteurs pourront évoluer afin de prendre en charge de nouveaux protocoles ou de nouvelles technologies, tout en conservant les principes d'abstraction, d'interopérabilité et d'indépendance définis dans le présent document.

L'ajout d'un nouveau fournisseur ne doit nécessiter aucune modification des applications métier ni des services transverses.

Autrement dit :

Application
      │
Service
      │
Contrat
      │
Connecteur
      │
Fournisseur