

Spécification fonctionnelle — Planning
Version de travail 1.0
1. Finalité
Le module Planning a pour objectif de fournir une vision temporelle des projets et de l’utilisation des ressources de l’entreprise.
Il répond principalement à deux enjeux :
•	respecter les engagements et délais des projets ; 
•	optimiser l’utilisation des ressources de l’entreprise, en anticipant les sous-charges, surcharges et indisponibilités. 
Le planning constitue un cadre prévisionnel d’organisation. Il ne cherche pas à imposer ou représenter tous les ajustements opérationnels réalisés sur le terrain.
Les écarts entre prévisionnel et réalisé sont constatés notamment au travers des rapports d’activité.
________________________________________
2. Un planning, quatre vues
Le système repose sur un même objet Planning, présenté sous quatre angles complémentaires.
Vue	Question traitée
Planning / Gantt	Quand ont lieu les projets, lots et tâches et comment s’enchaînent-ils ?
Planning ressources	Qui intervient où et quand ?
Plan de charge	Quelle capacité est disponible, consommée ou prévisionnelle ?
Calendrier	Quels jalons, réunions, absences et événements sont prévus ?
Les différentes vues utilisent les mêmes données et doivent rester cohérentes entre elles.
________________________________________
3. Situation à date
Le planning distingue le réalisé du prévisionnel à partir d’une date de situation.
                     Date de situation
                            │
       Réalisé              │          Prévisionnel
────────────────────────────┼────────────────────────────
Rapports d'activité         │ Planning
Activité constatée          │ Affectations
                            │ Charges prévues
                            │ Disponibilités futures
Pour le passé, les rapports d’activité constituent la source privilégiée de l’activité réellement effectuée.
Pour le futur, les données proviennent du planning prévisionnel.
Cette distinction doit notamment être utilisée dans le plan de charge.
________________________________________
4. Périmètre selon l’utilisateur
Profil	Périmètre
Administrateur client	Tous les projets de son environnement client
Chef de projet	Projets dont il a la responsabilité
Utilisateur	Projets auxquels il participe
Administrateur système	Projets accessibles au niveau système
Les vues multi-projets doivent permettre de sélectionner un projet particulier ou, lorsque les droits le permettent, de conserver une vision consolidée.
________________________________________
5. Planning / Gantt
La vue Planning présente graphiquement :
Projet
 └── Lot de travaux
      ├── Tâche
      ├── Tâche
      └── ...
Les différents niveaux peuvent être développés ou réduits sous forme d’accordéon.
Les barres affichent, lorsque l’espace disponible le permet :
CODE — Libellé
Le planning permet notamment d’afficher :
•	lots de travaux ; 
•	tâches ; 
•	jalons ; 
•	dépendances ; 
•	réunions. 
L’utilisateur peut sélectionner la période affichée et son niveau de détail temporel.
________________________________________
6. Dépendances et jalons
Le système doit permettre de définir des relations de dépendance entre les tâches et entre les lots de travaux.
Une modification susceptible d’avoir un impact sur le niveau supérieur n’est pas propagée silencieusement.
Par exemple :
Décalage d'une tâche
        ↓
Dépassement de la fin du lot
        ↓
Proposition de modification du lot
        ↓
Validation utilisateur
Le même principe s’applique entre un lot et son projet.
Les jalons matérialisent les dates ou échéances significatives du projet et disposent d’une représentation graphique spécifique.
________________________________________
7. Planification graphique
Le planning doit pouvoir constituer une véritable interface de saisie.
L’utilisateur doit notamment pouvoir :
•	déplacer graphiquement une tâche ; 
•	modifier sa durée par manipulation de sa barre ; 
•	déplacer un jalon ; 
•	créer ou modifier graphiquement des dépendances ; 
•	visualiser immédiatement les conséquences d’une modification. 
La saisie graphique et les formulaires traditionnels modifient les mêmes données métier.
L’objectif est de limiter les saisies clavier lorsque la manipulation graphique est plus naturelle.
________________________________________
8. Planning ressources
Cette vue présente le planning sous l’angle des personnes :
Ressource
 ├── Tâche A
 ├── Tâche B
 └── Tâche C
Elle répond principalement à la question :
Qui fait quoi et quand ?
Elle doit permettre une vision :
•	du jour ; 
•	de la semaine ; 
•	du mois ; 
•	d’un projet ; 
•	d’un ensemble de projets ; 
•	de l’ensemble des projets accessibles. 
Pour une ressource donnée, les affectations et indisponibilités sont présentées sur le même axe temporel.
________________________________________
9. Capacité d’une ressource
Le calcul de capacité doit prendre en compte au minimum :
Quotité de travail
Chaque employé dispose d’un taux représentant son activité contractuelle :
100 %  Temps plein
80 %   Temps partiel
50 %   Mi-temps
Indisponibilités
Le système permet d'enregistrer les indisponibilités prévisionnelles telles que :
•	congés ; 
•	formation ; 
•	absence ; 
•	autres indisponibilités. 
La capacité disponible résulte donc schématiquement de :
Capacité théorique
× quotité de travail
- indisponibilités
────────────────────
Capacité disponible
________________________________________
10. Charge affectée aux tâches
L’affectation d’une personne à une tâche doit permettre d’exprimer sa charge prévisionnelle.
Cette charge peut notamment être représentée par un taux d’affectation à la tâche.
Exemple :
Jean
Capacité : 35 h / semaine

Tâche A : 50 %
Tâche B : 30 %

Charge prévisionnelle : 80 %
Le planning doit conserver une certaine souplesse : ce taux constitue une intention de planification, et non l’obligation pour la personne de travailler mécaniquement selon cette répartition chaque jour.
Les ajustements opérationnels sont constatés ultérieurement par les rapports d’activité.
________________________________________
11. Plan de charge société
Le plan de charge consolide les charges provenant de l’ensemble des projets concernés.
Dans un premier temps, il porte sur les utilisateurs ayant le statut d’employé.
Il permet une analyse :
•	par personne ; 
•	par métier ; 
•	par projet ; 
•	par période ; 
•	pour l’ensemble de la société. 
Exemple :
Ressource	Capacité	Projet A	Projet B	Projet C	Charge	Occupation
Jean	35 h	21 h	14 h	—	35 h	100 %
Paul	35 h	28 h	14 h	—	42 h	120 %
Marc	28 h	7 h	7 h	—	14 h	50 %
Le regroupement par métier doit permettre une vision consolidée :
▾ Peintres                         92 %
    Jean                          100 %
    Paul                          120 %
    Marc                           50 %
Le système doit permettre d’anticiper :
•	les périodes de surcharge ; 
•	les périodes de sous-charge ; 
•	les conflits d’affectation ; 
•	les disponibilités futures. 
________________________________________
12. Calendrier
La vue Calendrier regroupe les événements ponctuels ou calendaires, notamment :
•	jalons ; 
•	réunions ; 
•	échéances ; 
•	indisponibilités ; 
•	éventuellement d’autres événements futurs. 
Les réunions existantes dans Easy Projet doivent pouvoir être intégrées sans devenir artificiellement des tâches.
________________________________________
13. Simulation
Le planning propose un mode simulation.
L’utilisateur peut modifier temporairement :
•	dates ; 
•	durées ; 
•	dépendances ; 
•	affectations ; 
•	répartition des ressources. 
Les conséquences sont calculées et affichées sans modifier immédiatement le planning de référence.
À l’issue de la simulation :
[ Abandonner ]       [ Appliquer les modifications ]
Les impacts significatifs doivent être présentés avant validation.
________________________________________
14. Assistance par IA
L’IA doit pouvoir être sollicitée pour proposer une optimisation du planning en tenant compte notamment :
•	des délais ; 
•	des dépendances ; 
•	des jalons ; 
•	des ressources disponibles ; 
•	des compétences/métiers ; 
•	des taux d’affectation ; 
•	des indisponibilités ; 
•	des charges provenant des autres projets. 
Elle pourra par exemple rechercher un compromis entre :
Respect des délais
        +
Disponibilité des ressources
        +
Limitation des surcharges
        +
Continuité des équipes
        +
Limitation des déplacements
L’IA ne modifie jamais directement le planning de référence.
Elle produit une proposition ou une simulation dont l’application nécessite une validation explicite de l’utilisateur.
________________________________________
15. Principe directeur
Le principe fonctionnel général du module est :
Le planning fournit un cadre d’organisation, d’anticipation et d’aide à la décision. Il ne doit pas devenir un carcan imposant la micro-organisation quotidienne des équipes.
Le prévisionnel donne une direction. Le terrain conserve sa souplesse. Les rapports d’activité permettent ensuite de confronter cette prévision à la réalité.
________________________________________
Je pense que cette V0.1 est suffisamment synthétique pour devenir notre document de référence, tout en laissant volontairement ouverts les choix de modèle de données, d'interface graphique et de moteur de calcul. La prochaine passe pourrait consister uniquement à identifier, à partir de cette spécification, les objets métier existants à modifier et les nouveaux objets à créer, sans encore écrire de code.




Oui, ces deux remarques doivent être intégrées : la première modifie réellement notre modèle d'autorisation du Planning, la seconde complète les fonctions transversales de navigation.
§4 — Périmètre selon l’utilisateur
Je remplacerais le tableau par :
Profil	Consultation	Modification
Administrateur client	Tous les projets de son environnement client	Selon ses droits d’administration
Chef de projet	Tous les projets de la société, notamment pour visualiser les conflits et partages de ressources	Projets dont il a la responsabilité
Utilisateur	Projets auxquels il participe	Selon ses droits sur le projet
Administrateur système	Tous les projets accessibles au niveau système	Selon ses droits système
C'est une distinction importante : le périmètre de lecture et le périmètre de modification du planning ne sont pas nécessairement identiques.
Pour le chef de projet, la lecture des autres projets est nécessaire précisément parce que la disponibilité d'une ressource ne peut pas être évaluée uniquement à partir de ses propres projets.
Par exemple, sur son projet A :
Jean
Projet A                         50 %
Autres projets                  40 %
────────────────────────────────────
Occupation société              90 %
Il doit donc pouvoir comprendre d'où viennent les 40 % supplémentaires, tout en ne pouvant pas modifier les projets concernés.
Sélection calendaire
Je l'ajouterais comme fonction commune aux quatre vues, plutôt que seulement dans le Gantt.
Le Planning doit permettre de sélectionner librement la période observée :
Du [ 17/08/2026 ] au [ 30/09/2026 ]

[ Aujourd'hui ] [ Semaine ] [ Mois ] [ Trimestre ]
avec navigation :
[ ‹ ]     Août — Septembre 2026     [ › ]
La granularité d'affichage doit pouvoir s'adapter à la période :
Quelques jours     → heures / jours
Quelques semaines  → jours / semaines
Quelques mois      → semaines / mois
Longue période     → mois / trimestres
Je prévoirais également « Aujourd'hui » comme action permanente pour revenir immédiatement à la date courante.
Et surtout, la période sélectionnée doit être conservée lorsque l'on change de vue :
Gantt
   ↓
Ressources
   ↓
Plan de charge
   ↓
Calendrier
Si je travaille sur 01/09 → 30/09, passer de Gantt à Ressources ne doit pas me ramener arbitrairement sur une autre période.
Avec ces deux corrections, je considérerais la V0.1 validée fonctionnellement et je passerais à une V0.2 consolidée avant d'aborder les objets métier.



