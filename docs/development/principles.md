

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
