# 13 — ClientEnvironment, licences et accès aux projets

## 1. Objet

Ce document fixe les principes structurants relatifs :

- au `ClientEnvironment` ;
- aux licences ;
- à la création des projets ;
- au périmètre de visibilité et de modification des utilisateurs.

Ces principes doivent être considérés comme des règles d'architecture stables. Toute évolution ultérieure doit les préserver ou faire l'objet d'une décision d'architecture explicite.

---

## 2. ClientEnvironment

Un `ClientEnvironment` représente le périmètre client contractuel, fonctionnel et technique d'Easy Projet.

Il est défini par :

```text
Société cliente
    +
une ou plusieurs licences
    =
ClientEnvironment
```

Le `ClientEnvironment` constitue le périmètre principal d'isolation des données.

Il ne représente pas :

- un projet ;
- une affectation utilisateur ;
- une simple relation entre une société et un utilisateur.

Il représente l'espace client dans lequel sont gérés les projets, les licences, les utilisateurs autorisés et les données associées.

---

## 3. Société et environnement client

Une `Company` représente une société réelle.

Un `ClientEnvironment` représente l'environnement Easy Projet attribué à une société cliente.

Relation cible :

```text
Company 1 ── 0..1 ClientEnvironment
```

Dans la version actuelle du modèle commercial, une société cliente possède au plus un environnement client actif.

Cette règle pourra évoluer uniquement si un besoin réel justifie plusieurs environnements distincts pour une même société.

---

## 4. Licences

### 4.1 Principe commercial actuel

Le contrat commercial actuel est :

```text
1 licence = 1 projet
```

Un client peut acheter plusieurs licences en une seule commande.

Exemple :

```text
Achat de 10 licences
    ↓
10 licences disponibles
    ↓
jusqu'à 10 projets créables
```

Les licences sont rattachées au `ClientEnvironment`.

### 4.2 Capacité d'une licence

Le modèle doit permettre une évolution future vers une licence couvrant plusieurs projets.

Exemple futur :

```text
1 licence globale = 10 projets
```

Pour éviter une refonte ultérieure, une licence porte une capacité :

```text
project_capacity
```

Dans le contrat actuel :

```text
project_capacity = 1
```

Dans un contrat futur :

```text
project_capacity = 10
```

Relation cible :

```text
ClientEnvironment 1 ── N License
License 1 ── 0..N Project
```

La règle métier impose :

```text
nombre de projets liés à une licence
    ≤
project_capacity
```

### 4.3 États d'une licence

Les états minimaux sont :

| État | Signification |
|---|---|
| `WAITING` | Licence disponible, avec une capacité non consommée |
| `ACTIVE` | Licence utilisée au moins partiellement |
| `EXPIRED` | Licence non utilisable |

L'état d'une licence ne remplace pas le calcul de sa capacité disponible.

Une licence `ACTIVE` peut encore accepter un projet si sa capacité n'est pas entièrement consommée.

---

## 5. Création d'un projet

La création d'un projet dépend de la disponibilité d'une licence.

Le processus est le suivant :

```text
Demande de création d'un projet
    ↓
Recherche d'une licence valide
    ↓
Vérification de la capacité disponible
    ↓
Affectation de la licence au projet
    ↓
Création du projet
```

La création doit être refusée si aucune licence valide ne dispose d'une capacité disponible.

Cette opération doit être réalisée dans une transaction atomique afin d'éviter qu'une même capacité soit consommée simultanément par plusieurs créations de projet.

La logique de sélection et d'affectation de la licence appartient à un service métier dédié.

Elle ne doit pas être placée :

- dans un template ;
- dans un formulaire ;
- directement dans une vue ;
- dans le modèle `Project` seul.

---

## 6. Utilisateur et société d'appartenance

Le champ :

```text
User.company
```

représente la société d'appartenance ou l'employeur de l'utilisateur.

Il ne représente pas nécessairement le `ClientEnvironment` auquel l'utilisateur peut accéder.

Exemple :

- un sous-traitant appartient à sa propre société ;
- il peut être affecté à un projet appartenant au `ClientEnvironment` d'une société cliente.

L'accès à Easy Projet ne doit donc pas être déduit uniquement de `User.company`.

---

## 7. Principes d'accès aux projets

Les règles d'accès distinguent toujours :

- la visibilité ;
- la modification.

Voir un projet ne signifie pas nécessairement pouvoir le modifier.

### 7.1 Administrateur système

L'administrateur système dispose d'un accès transversal aux environnements clients selon les règles d'administration d'Easy Projet.

Son accès ne dépend pas :

- de sa société ;
- d'une licence ;
- d'une affectation projet.

### 7.2 Administrateur client

L'administrateur client est rattaché à la société cliente.

Il accède à tous les projets du `ClientEnvironment`.

Périmètre :

```text
lecture : tous les projets
écriture : tous les projets
```

Il n'est pas nécessaire de l'affecter individuellement à chaque projet.

Cette règle justifie que l'administrateur client ne soit pas lié directement à un projet.

### 7.3 Chef de projet

Le chef de projet voit tous les projets du `ClientEnvironment`.

Périmètre :

```text
lecture : tous les projets
écriture : uniquement les projets dont il a la responsabilité
```

La responsabilité d'un projet doit être représentée explicitement.

Elle ne doit pas être déduite d'un simple rôle global.

### 7.4 Utilisateur

Un utilisateur standard accède uniquement aux projets auxquels il est affecté.

Son périmètre exact dépend des droits portés par son affectation au projet.

### 7.5 Sous-traitant

Un sous-traitant accède uniquement aux projets auxquels il est affecté.

Son accès doit rester limité au périmètre qui lui est explicitement attribué.

Il ne doit jamais obtenir automatiquement l'accès à tous les projets du `ClientEnvironment` en raison de sa société d'appartenance.

---

## 8. Résolution des droits

Les droits doivent être résolus à partir de plusieurs éléments :

```text
rôle global
    +
société de l'utilisateur
    +
ClientEnvironment
    +
affectations aux projets
    +
responsabilité éventuelle du projet
```

Cette résolution appartient à un service ou à une politique d'autorisation dédiée.

Elle ne doit pas être dupliquée dans chaque vue.

---

## 9. Rôle d'EPContext

`EPContext` représente le contexte d'exécution courant du framework.

Il peut contenir :

```text
operator
client_environment
company
project
```

Les responsabilités restent distinctes :

- `operator` : utilisateur courant ;
- `client_environment` : environnement client actif ;
- `company` : société utile dans le contexte courant ;
- `project` : projet courant, lorsqu'il existe.

`ClientEnvironment` ne doit pas devenir un objet fourre-tout contenant l'utilisateur courant, le projet courant ou les permissions calculées.

---

## 10. Ordre de construction

L'ordre fonctionnel retenu est :

```text
Company
    ↓
ClientEnvironment
    ↓
License
    ↓
Project
    ↓
ProjectAssignment
```

Cet ordre permet :

- de définir l'environnement client ;
- de lui rattacher ses licences ;
- de vérifier la capacité disponible avant de créer un projet ;
- de gérer ensuite les affectations et les droits.

---

## 11. Contraintes à préserver

Les règles suivantes sont considérées comme structurantes :

1. un projet appartient toujours à un `ClientEnvironment` ;
2. un projet consomme une capacité de licence ;
3. la création d'un projet est impossible sans capacité disponible ;
4. l'administrateur client n'a pas besoin d'une affectation projet ;
5. le chef de projet voit tous les projets, mais ne modifie que ceux dont il est responsable ;
6. les utilisateurs standards et sous-traitants accèdent uniquement aux projets auxquels ils sont affectés ;
7. `User.company` représente la société d'appartenance, pas le périmètre d'accès ;
8. la visibilité et l'écriture sont deux notions distinctes ;
9. les règles d'accès doivent être centralisées ;
10. toute modification de ces principes doit être documentée avant mise en œuvre.

---

## 12. Modèle conceptuel synthétique

```text
Company
   │
   └── 0..1 ClientEnvironment
              │
              ├── 1..N License
              │       │
              │       └── 0..N Project
              │
              └── 0..N Project
                      │
                      ├── responsable
                      └── affectations utilisateurs
```

```text
User
   ├── appartient à une Company
   ├── possède un rôle global
   └── peut être affecté à un ou plusieurs Project
```

---

## 13. Décisions reportées

Les sujets suivants ne sont pas définis dans ce document :

- facturation ;
- renouvellement automatique ;
- tarification ;
- suspension temporaire ;
- transfert d'une licence entre environnements ;
- plusieurs environnements pour une même société ;
- quotas autres que le nombre de projets ;
- règles fines d'affectation des sous-traitants.

Ils seront traités lorsqu'un besoin fonctionnel concret apparaîtra.
