

# Framework des listes

## 1. Objet du document

Ce document décrit l’architecture validée du framework de listes d’Easy Projet.

Il présente les responsabilités des composants, leurs relations et les règles à respecter lors de la création d’une nouvelle liste métier.

Il ne constitue ni un journal de conception ni une feuille de route. Il contient uniquement les principes retenus et les fonctionnalités effectivement implémentées.

---

## 2. Objectif du framework

Le framework de listes fournit une infrastructure commune pour afficher des collections de données dans Easy Projet.

Il doit permettre de :

* décrire une liste à partir d’une définition centralisée ;
* identifier les colonnes disponibles et visibles ;
* extraire les valeurs depuis des objets ou des dictionnaires ;
* trier les données ;
* paginer les résultats ;
* construire un modèle de présentation indépendant du modèle métier ;
* limiter la duplication entre les différents modules de l’application.

Les listes de sociétés, projets, documents, réunions ou autres entités doivent pouvoir utiliser la même architecture.

Le framework applique le principe de **généricité maîtrisée** : il centralise les comportements communs sans chercher à rendre génériques les particularités métier qui ne le justifient pas.

---

## 3. Principes d’architecture

### 3.1 Single Source of Truth

La définition d’une liste constitue la source de vérité pour sa structure.

Elle précise notamment :

* l’entité concernée ;
* les colonnes disponibles ;
* les colonnes visibles ;
* l’ordre des colonnes ;
* les colonnes triables ;
* le tri par défaut ;
* la taille de page par défaut.

Le template ne doit pas redéfinir indépendamment les colonnes de la liste.

Une modification de structure doit être réalisée dans la définition de liste, puis propagée par le framework jusqu’au modèle de présentation.

### 3.2 Séparation des responsabilités

Le framework distingue trois niveaux :

1. **Définition**
   Décrit ce qu’est la liste.

2. **Exécution**
   Applique la définition à un ensemble de données.

3. **Présentation**
   Prépare des objets adaptés au rendu dans une vue.

Cette séparation évite de mélanger :

* les règles structurelles ;
* la manipulation des données ;
* les besoins d’affichage ;
* les particularités de Django ;
* les règles métier propres à une application.

### 3.3 Indépendance technologique

Le cœur du framework de listes ne produit pas de HTML et ne dépend pas des templates Django.

`EPList`, `ListPage` et les modèles de présentation sont des objets Python indépendants du moteur de rendu.

L’intégration avec Django est réalisée dans la vue applicative.

### 3.4 Validation précoce

Les définitions et les paramètres d’exécution sont validés avant utilisation.

Les erreurs de structure ou de type doivent être détectées au plus tôt, avec des messages explicites.

### 3.5 Immutabilité des modèles de présentation

Les modèles de présentation sont définis comme des dataclasses immuables.

Ils représentent un instantané cohérent de la liste au moment de son rendu.

Cette immutabilité évite qu’une colonne, une ligne ou une pagination soit modifiée accidentellement après sa construction.

### 3.6 Absence de logique métier dans le framework

Le framework ne décide pas :

* si une société est active ou inactive ;
* comment afficher un statut métier ;
* quelles actions sont autorisées ;
* quelle URL doit être utilisée pour modifier un objet ;
* quels droits possède l’opérateur courant.

Ces responsabilités restent dans l’application métier ou dans une couche de présentation spécialisée.

---

## 4. Architecture générale

Le framework suit le flux suivant :

                         ListDefinition
                                |
                                | validation
                                v
                             EPList
                  tri / pagination / extraction
                                |
                                | produit
                                v
                            ListPage
                                |
                                v
                    ListViewModelBuilder
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
        ViewColumn           ViewRow      PaginationViewModel
                                |
                                v
                            ViewCell
                                |
                                v
                       Template Django

Les composants sont répartis dans plusieurs packages :

framework/
├── list/
│   ├── column.py
│   ├── definition.py
│   └── validator.py
│
├── runtime/
│   └── eplist.py
│
└── viewmodel/
    ├── builder.py
    ├── cell.py
    ├── column.py
    ├── list.py
    ├── pagination.py
    └── row.py

---

## 5. Couche de définition

### 5.1 `ListDefinition`

`ListDefinition` décrit la structure d’une liste.

Elle constitue la source de vérité utilisée par l’exécution et la présentation.

Elle fournit notamment :

* l’entité associée ;
* la collection de colonnes ;
* les colonnes visibles ;
* le tri par défaut ;
* la taille de page par défaut ;
* les méthodes de recherche d’une colonne.

`ListDefinition` ne manipule pas les données métier.

Elle ne trie pas, ne pagine pas et ne produit pas de modèle de présentation.

### 5.2 `ColumnDefinition`

`ColumnDefinition` décrit une colonne de liste.

Une colonne est reliée à un champ de l’entité et possède des propriétés de présentation et de comportement.

Elle peut notamment indiquer :

* son identifiant ;
* son libellé ;
* sa visibilité ;
* son ordre ;
* sa largeur ;
* sa capacité à être triée.

La définition d’une colonne reste déclarative. Elle ne contient pas la valeur d’une cellule pour une ligne donnée.

### 5.3 Validation de la définition

La définition est validée par `ListValidator`.

La validation intervient lors de la création d’une instance de `EPList`.

Une liste invalide ne doit pas pouvoir être exécutée.

Cette validation garantit notamment la cohérence de la structure avant toute opération de tri, de pagination ou de construction du modèle de présentation.

---

## 6. Couche d’exécution

### 6.1 `EPList`

`EPList` applique une `ListDefinition` à un ensemble de données.

Sa création nécessite :

* une définition de liste ;
* un itérable de lignes sources.

Les lignes sources sont converties en tuple afin de fournir un état stable pendant l’exécution.

### 6.2 Responsabilités de `EPList`

`EPList` est responsable de :

* valider le type de la définition ;
* valider que les données sont itérables ;
* déclencher la validation de la définition ;
* exposer les colonnes déclarées ;
* exposer les colonnes visibles ;
* conserver les lignes sources ;
* extraire une valeur depuis une ligne ;
* trier les lignes ;
* paginer les lignes ;
* produire une instance de `ListPage`.

### 6.3 Responsabilités exclues

`EPList` ne doit pas :

* produire du HTML ;
* construire une réponse Django ;
* connaître les templates ;
* appliquer des règles d’autorisation ;
* construire des badges ou des composants visuels ;
* générer des liens d’action ;
* contenir de logique métier propre à une entité.

### 6.4 Types de lignes supportés

`EPList.get_value()` accepte actuellement deux formes de données :

* un objet possédant un attribut correspondant au nom du champ ;
* un mapping contenant une clé correspondant au nom du champ.

Exemple conceptuel :

```text
Objet Django
    company.name

Mapping
    company["name"]
```

Cette règle permet au framework de fonctionner avec des modèles Django, des objets Python ou des dictionnaires.

Une erreur d’exécution est levée lorsqu’un champ attendu est absent.

### 6.5 Tri

La méthode `sort_rows()` trie les données en utilisant :

* le paramètre `sort_by`, lorsqu’il est fourni ;
* sinon le tri par défaut de la définition ;
* sinon l’ordre initial des lignes.

Une colonne utilisée pour le tri doit :

* exister dans la définition ;
* être déclarée comme triable.

Les valeurs `None` sont conservées à la fin du résultat.

Si les valeurs ne peuvent pas être comparées entre elles, une `EPListExecutionError` est levée.

### 6.6 Pagination

La méthode `paginate()` effectue successivement :

1. la validation du numéro de page ;
2. la détermination de la taille de page ;
3. le tri des lignes ;
4. le calcul du nombre total d’éléments ;
5. le calcul du nombre total de pages ;
6. l’extraction des lignes de la page demandée ;
7. la construction d’un `ListPage`.

La taille de page utilisée provient :

* du paramètre `page_size`, lorsqu’il est fourni ;
* sinon de la taille définie dans `ListDefinition`.

---

## 7. `ListPage`

`ListPage` représente le résultat paginé produit par `EPList`.

Il contient :

* les lignes de la page courante ;
* le numéro de la page ;
* la taille de page ;
* le nombre total d’éléments ;
* le nombre total de pages ;
* l’existence d’une page précédente ;
* l’existence d’une page suivante.

`ListPage` est indépendant du système de pagination Django.

Il ne possède aucune méthode de rendu.

---

## 8. Couche de présentation

### 8.1 Objectif

La couche `viewmodel` transforme les données d’exécution en objets adaptés à une vue.

Elle évite au template de manipuler directement les définitions techniques ou de reconstruire lui-même la structure de la liste.

### 8.2 `ListViewModelBuilder`

`ListViewModelBuilder` construit un `ListViewModel` à partir de :

* une instance de `EPList` ;
* une instance de `ListPage` ;
* l’identifiant du tri courant ;
* le sens du tri.

Il produit un instantané complet de présentation.

Le builder réalise les opérations suivantes :

1. validation des paramètres ;
2. détermination du tri effectif ;
3. construction des colonnes de présentation ;
4. construction des lignes ;
5. construction des cellules ;
6. construction de la pagination ;
7. assemblage du `ListViewModel`.

### 8.3 Construction des colonnes

Chaque colonne visible de `EPList` devient une instance de `ViewColumn`.

Le builder indique également :

* si la colonne est actuellement triée ;
* si le tri est descendant.

Les colonnes non visibles ne sont pas transmises au modèle de présentation.

### 8.4 Construction des lignes

Chaque ligne contenue dans `ListPage.rows` devient une instance de `ViewRow`.

La ligne de présentation contient :

* les cellules correspondant aux colonnes visibles ;
* l’objet source ayant servi à construire la ligne.

L’objet source est conservé pour les besoins métier qui ne sont pas encore génériques, par exemple :

* générer l’URL de modification ;
* vérifier un état métier ;
* afficher une action spécifique.

### 8.5 Construction des cellules

Pour chaque colonne visible, le builder :

1. demande à `EPList` d’extraire la valeur ;
2. construit une instance de `ViewCell`.

Dans l’implémentation actuelle :

```text
value == display_value
```

Le framework ne réalise donc pas encore de formatage spécifique des valeurs.

### 8.6 Construction de la pagination

Le builder transforme `ListPage` en `PaginationViewModel`.

Il calcule notamment :

* le numéro de la page précédente ;
* le numéro de la page suivante.

Ces valeurs sont absentes lorsqu’aucune page correspondante n’existe.

---

## 9. Modèles de présentation

### 9.1 `ListViewModel`

`ListViewModel` constitue le modèle de présentation complet d’une liste.

Il contient :

* un tuple de `ViewColumn` ;
* un tuple de `ViewRow` ;
* un `PaginationViewModel`.

Il vérifie qu’une ligne contient exactement une cellule pour chaque colonne visible.

`ListViewModel` peut être parcouru directement. Son itération retourne ses lignes.

### 9.2 `ViewColumn`

`ViewColumn` représente une colonne préparée pour la vue.

Il encapsule la `ColumnDefinition` d’origine et expose les informations nécessaires au rendu, notamment :

* l’identifiant ;
* le libellé ;
* la visibilité ;
* la capacité de tri ;
* la largeur ;
* l’ordre ;
* l’état du tri ;
* le sens du tri.

Le template utilise le libellé exposé par `ViewColumn` et non une définition locale.

### 9.3 `ViewRow`

`ViewRow` représente une ligne préparée pour la vue.

Il contient :

* un tuple de `ViewCell` ;
* l’objet source.

Il peut être parcouru directement. Son itération retourne ses cellules.

### 9.4 `ViewCell`

`ViewCell` représente la valeur d’une colonne pour une ligne donnée.

Il contient :

* la valeur brute ;
* la valeur d’affichage ;
* la colonne associée.

La colonne permet notamment de connaître l’identifiant et les caractéristiques de la cellule.

Dans la version actuelle, la valeur brute et la valeur d’affichage sont identiques.

### 9.5 `PaginationViewModel`

`PaginationViewModel` contient les informations de pagination utiles à une vue :

* page courante ;
* taille de page ;
* nombre total d’éléments ;
* nombre total de pages ;
* présence d’une page précédente ;
* présence d’une page suivante ;
* numéro de la page précédente ;
* numéro de la page suivante.

Il contrôle la cohérence entre les indicateurs booléens et les numéros de pages associés.

---

## 10. Intégration avec Django

### 10.1 Responsabilité de la vue applicative

La vue Django assure le lien entre :

* le queryset ou la collection métier ;
* la définition de liste ;
* `EPList` ;
* la pagination ;
* `ListViewModelBuilder` ;
* le contexte du template.

Le framework ne dépend pas directement de `ListView`.

### 10.2 Intégration actuelle de la liste des sociétés

La liste des sociétés utilise encore la pagination native de `ListView`.

La vue :

1. récupère la page Django courante ;
2. crée une instance de `EPList` avec les objets de cette page ;
3. adapte les informations de pagination Django en `ListPage` ;
4. construit le `ListViewModel` ;
5. place le résultat dans le contexte sous le nom `list`.

Cette intégration permet de valider progressivement le framework sans remplacer simultanément toute la pagination existante.

### 10.3 Utilisation dans le template

Le template utilise :

```text
list.columns
```

pour afficher les en-têtes.

Il utilise :

```text
list.rows
```

pour parcourir les lignes.

Les valeurs simples sont lues depuis :

```text
row.cells.<index>.display_value
```

L’objet source reste accessible depuis :

```text
row.source_object
```

Il est utilisé actuellement pour :

* l’état actif ou inactif de la société ;
* l’identifiant nécessaire à l’action de modification.

### 10.4 Accès positionnel aux cellules

Les cellules sont actuellement accessibles par leur position :

```text
row.cells.0
row.cells.1
row.cells.2
```

Cette solution est acceptée pour les templates métier dont la structure est stable.

Elle implique cependant que l’ordre du template reste cohérent avec l’ordre des colonnes visibles de la définition.

Un mécanisme d’accès par identifiant ne sera ajouté que lorsqu’un besoin réel justifiera cette complexité supplémentaire.

---

## 11. Gestion des particularités métier

Certaines cellules ne peuvent pas être rendues par un simple affichage de `display_value`.

La colonne `is_active` de la liste des sociétés en est un exemple.

La valeur métier :

```text
True / False
```

est affichée sous forme de badge :

```text
Active / Inactive
```

avec des classes visuelles distinctes.

Dans l’implémentation actuelle, cette logique reste dans le template et utilise `row.source_object`.

Ce choix est volontaire :

* le besoin est métier ;
* aucun mécanisme générique de formatage n’est encore validé ;
* le framework ne doit pas être complexifié par anticipation.

Les actions de ligne restent également spécifiques au template, notamment l’action de modification d’une société.

---

## 12. Décisions validées

Les décisions suivantes sont considérées comme validées.

### 12.1 Une définition centralisée par liste

La structure d’une liste est définie dans une `ListDefinition`.

Les colonnes ne doivent pas être redéclarées indépendamment dans la vue et dans le template.

### 12.2 Séparation définition, exécution et présentation

Les responsabilités sont réparties entre :

```text
ListDefinition
EPList
ListViewModelBuilder
ListViewModel
```

Aucun de ces composants ne doit absorber les responsabilités des autres couches.

### 12.3 Réutilisation de `ViewColumn`

Le framework possède un unique modèle de présentation pour les colonnes.

Aucun second objet équivalent ne doit être créé.

### 12.4 Utilisation de structures immuables

Les modèles de présentation sont construits sous forme de dataclasses gelées et utilisent des tuples.

### 12.5 Conservation temporaire de l’objet source

`ViewRow.source_object` est conservé afin de permettre les actions et rendus métier qui ne sont pas encore généralisés.

### 12.6 Généricité progressive

Le framework évolue uniquement à partir de besoins réels rencontrés dans les modules métier.

Un mécanisme générique ne doit pas être ajouté uniquement parce qu’il pourrait devenir utile ultérieurement.

### 12.7 Tests unitaires par composant

Les composants de la couche `viewmodel` possèdent leurs propres tests unitaires :

```text
test_builder.py
test_cell.py
test_column.py
test_list.py
test_pagination.py
test_row.py
```

Toute évolution du framework doit maintenir ou compléter cette couverture.

---

## 13. Règles d’utilisation pour une nouvelle liste

Pour ajouter une nouvelle liste métier :

1. définir l’entité et ses champs dans le dictionnaire métier ;
2. créer une `ListDefinition` ;
3. déclarer les colonnes et leur ordre ;
4. définir les colonnes visibles ;
5. définir le tri par défaut ;
6. créer une instance de `EPList` dans la vue ;
7. produire ou adapter une instance de `ListPage` ;
8. construire un `ListViewModel` avec `ListViewModelBuilder` ;
9. transmettre le modèle de présentation au template ;
10. conserver dans le template uniquement les particularités réellement métier.

Le template ne doit pas recalculer la structure de la liste.

---

## 14. Limites actuelles

La version actuelle du framework ne prend pas encore en charge de manière générique :

* le formatage des dates ;
* le formatage des montants ;
* le formatage des booléens ;
* les badges de statut ;
* les colonnes calculées ;
* les actions de ligne ;
* les filtres de recherche ;
* les exports ;
* l’accès aux cellules par identifiant ;
* la sélection dynamique de la taille de page dans le ViewModel.

Ces éléments ne constituent pas des fonctionnalités promises.

Ils devront être étudiés uniquement lorsqu’un cas métier concret le nécessitera.

---

## 15. Constantes de pagination

Le nombre de lignes par page apparaît actuellement dans plusieurs contextes, notamment :

```text
paginate_by
list_per_page
page_size
```

Le besoin de centraliser les constantes communes de pagination a été identifié.

La décision d’architecture retenue est la suivante :

* une valeur générique commune pourra être définie dans les constantes partagées ;
* une `ListDefinition` peut conserver sa propre taille par défaut lorsqu’une liste possède un besoin spécifique ;
* l’administration Django peut réutiliser la constante commune ;
* la centralisation ne doit pas supprimer la possibilité de surcharge locale.

Cette centralisation n’est pas traitée dans la présente version du framework.

---

## 16. Maintenance du document

Ce document doit évoluer en même temps que le framework.

Une nouvelle fonctionnalité n’y est ajoutée que lorsqu’elle est :

* validée ;
* implémentée ;
* testée ;
* intégrée à au moins un cas d’utilisation réel.

Les idées, hypothèses et options non retenues ne doivent pas être conservées dans ce document.
