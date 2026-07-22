

# 1 Objet

Le présent document définit les règles permettant d'échanger avec des services ou applications tiers tout en garantissant l'indépendance et la pérennité de l'architecture.
Easy Projet dépend de contrats d'échange, jamais de produits ou de fournisseurs.

# 2 Rôle des connecteurs externes

Les connecteurs externes assurent les échanges entre Easy Projet et les systèmes tiers.

Ils sont responsables de :

- traduire les demandes internes vers le protocole attendu par le système externe ;
- recevoir et interpréter les réponses ;
- isoler les spécificités techniques des fournisseurs ;
- garantir la stabilité des échanges.

Les applications métier ne communiquent jamais directement avec un système externe.

# 3 Principes de conception

Les connecteurs externes reposent sur les principes suivants :

- les applications métier dépendent de contrats d'échange et non de fournisseurs ;
- chaque technologie externe est isolée dans un composant dédié ;
- les interfaces de communication sont stables, documentées et, lorsque cela est possible, fondées sur des protocoles normalisés ;
- un fournisseur peut être remplacé sans modifier les applications métier ;
- les échanges doivent être sécurisés, traçables et maîtrisés ;
- les contraintes techniques, contractuelles ou organisationnelles imposées par un client doivent pouvoir être prises en compte sans remettre en cause l'architecture globale.

# 4 Organisation des connecteurs

Les connecteurs sont organisés par capacité fonctionnelle et non par produit.

                    Easy Projet
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

Les implémentations citées sont données à titre d'exemple. Elles ne constituent pas des choix d'architecture.

# 5 Règles d'utilisation

Les règles suivantes s'appliquent à l'ensemble des connecteurs :

- toute communication avec un système externe passe par un connecteur dédié ;
- un connecteur ne traite que les échanges avec le système qu'il représente ;
- les applications métier ignorent la technologie utilisée par le fournisseur ;
- les protocoles de communication doivent être documentés et respectés ;
- les erreurs et indisponibilités des systèmes externes doivent être maîtrisées sans compromettre la stabilité d'Easy Projet ;
- toute évolution ou remplacement d'un fournisseur doit être limité au connecteur concerné.

# 6 Évolutions

L'architecture des connecteurs est conçue pour intégrer de nouveaux services ou remplacer des fournisseurs existants sans modifier les applications métier.

Les connecteurs pourront évoluer afin de prendre en charge de nouveaux protocoles ou de nouvelles technologies, tout en conservant les principes d'abstraction, d'interopérabilité et d'indépendance définis dans le présent document.