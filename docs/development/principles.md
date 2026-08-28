

# Principes de développement Easy Projet

## 1. Le métier prime sur la technique

Le métier constitue la référence principale du projet.
Django, PostgreSQL et les choix techniques doivent traduire fidèlement le modèle métier, et non l'inverse.

## 2. Le code découle du modèle

Le code applicatif est la conséquence du modèle fonctionnel, du MCD, du dictionnaire de données et des règles métier.

Si le développement met en évidence une amélioration nécessaire du modèle, le modèle est modifié avant que le code ne soit figé.

## 3. Les documents de conception sont vivants

Les documents de conception servent de référence, mais ne sont pas un carcan.
Ils peuvent évoluer lorsque la réflexion métier ou technique progresse.

## 4. Un sujet terminé avant d'en ouvrir un autre

Chaque sujet de développement doit être conçu, développé, testé et documenté avant d'ouvrir un nouveau sujet.

## 5. Une responsabilité par composant

Chaque app, fichier, classe ou fonction doit avoir une responsabilité claire.

## 6. Ne jamais dupliquer le code

Tout code utilisé plusieurs fois doit être analysé pour déterminer s'il doit devenir générique.

## 7. Privilégier les composants génériques

Les listes, formulaires, tableaux de bord, composants de sélection et services transverses doivent être conçus de manière réutilisable dès que cela est pertinent.

## 8. Utiliser les mécanismes standards de Django

Les fonctionnalités natives de Django sont privilégiées avant toute solution spécifique.

## 9. Documenter les décisions importantes

Toute décision structurante doit être tracée dans une ADR.

## 10. Une seule source de vérité

Les constantes techniques, règles transverses, modèles abstraits et catalogues doivent être centralisés pour éviter les divergences.


II. Design System
## 11. Les composants ne contiennent aucune logique métier

Les composants du Design System Easy Projet sont uniquement responsables de la présentation.

Ils reçoivent leur configuration des modèles, formulaires ou du contexte d'utilisation.

Ils ne prennent aucune décision métier.

## 12. Les composants sont stateless

Les composants ne stockent aucun état fonctionnel.

Ils affichent les données qui leur sont fournies.

## 13. Les composants sont configurables

Les caractéristiques d'un champ (label, longueur, validation, aide, etc.) proviennent du modèle ou du formulaire, jamais du composant.

## 14. Responsive dès la conception

Chaque composant doit définir son comportement sur PC, tablette et téléphone.

## 15. Compatible thème clair / sombre

Tout composant du Design System doit être utilisable dans les deux thèmes.

## 16. Le dictionnaire de données est la référence

Le dictionnaire décrit non seulement la structure des données mais également leur représentation dans l'interface (widget et propriétés).

Toute évolution d'un composant commence par la mise à jour du dictionnaire.

## 17. Les composants ignorent le métier

Un composant graphique Easy Projet ne contient aucune connaissance métier.

Il reçoit uniquement une configuration et produit une représentation graphique.

18. Un même concept utilise un même composant

Deux fonctionnalités présentant le même concept fonctionnel doivent utiliser le même composant générique.

Une différence de données, de configuration ou de règle métier ne justifie pas la création d'un nouveau composant graphique.

19. La variabilité relève de la configuration

Les différences entre les usages d'un composant doivent, autant que possible, être exprimées par sa configuration.

Par exemple, une liste peut disposer ou non de filtres, d'actions, d'une pagination ou d'une ligne de synthèse sans constituer un nouveau type de liste.

De même, un formulaire peut comporter une ou plusieurs sections et zéro, une ou plusieurs collections associées sans nécessiter une architecture différente.

20. Un composant spécifique répond à une interaction spécifique

Un composant spécifique n'est créé que lorsque la nature de l'interaction utilisateur ne peut raisonnablement être représentée par un composant générique.

Sont notamment susceptibles de relever de composants spécifiques : cartographie, tableaux de bord, planning, reporting, conversation et interactions avec un assistant IA.

La spécificité métier seule ne suffit pas à justifier un composant spécifique.

21. Les composants spécifiques suivent l'architecture commune

Un composant spécifique conserve les mêmes principes d'organisation que les composants génériques.

Il reprend, lorsque cela est applicable, le même découpage en définition, runtime, ViewModel, intégration, templates, ressources statiques et tests.

La spécificité fonctionnelle ne doit pas entraîner une nouvelle architecture technique.

22. Les écrans métier assemblent les composants

Les templates et vues métier configurent et assemblent les composants du Design System.

Ils ne doivent pas reproduire localement la présentation, les comportements ou les structures déjà fournis par un composant générique.

23. Toute exception doit être justifiée

Avant de créer un nouveau composant, template, comportement ou mécanisme spécifique, il faut vérifier si le besoin peut être couvert par l'extension configurable d'un composant existant.

Une exception est introduite uniquement lorsqu'elle correspond à une différence fonctionnelle réelle et durable.