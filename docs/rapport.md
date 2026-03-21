# Rapport de projet

## Groupe 1
* Amel BEN CHABANE 21304456
* Tassadit AKSAS 21302943

## Description des choix importants d'implémentation

Dans ce projet, nous avons étudié différentes stratégies de prise de décision dans un environnement multi-agents simulé avec PySpriteWorld. Deux équipes de joueurs s'affrontent afin de capturer des fioles, chaque type de fiole ayant des règles spécifiques de collecte.

L'objectif est d'analyser les performances relatives de différentes stratégies dans un contexte compétitif, dynamique et dépendant de la coordination entre agents.

### Structure générale du programme

Le programme repose sur une simulation multi-épisodes dans laquelle deux équipes s'affrontent. À chaque épisode :

- chaque équipe sélectionne une stratégie,
- les joueurs choisissent des fioles à atteindre,
- ils se déplacent via A* jusqu'à une position autour des fioles,
- les scores sont calculés selon les règles associées à chaque couleur.

Les stratégies influencent directement la sélection des fioles, ce qui impacte fortement les résultats.

### Structure des fichiers

Le projet est structuré en plusieurs fichiers principaux :

- **main.py** :  
  Point d'entrée du programme. Il permet de lancer des simulations complètes en testant toutes les combinaisons de stratégies sur plusieurs cartes.

- **strategies.py** :  
  Contient l'ensemble des stratégies implémentées. Chaque stratégie retourne un choix de fioles pour les joueurs, en fonction de paramètres comme les regrets ou l'historique.

### Simulation et collecte des données

Les simulations sont réalisées sur plusieurs épisodes (10 par défaut), avec :

- alternance de priorité entre les équipes,
- mise à jour des regrets après chaque épisode,
- stockage de l'historique des choix.

Pour chaque confrontation stratégie A vs stratégie B, on obtient :

- un score total par équipe,
- une trace des performances sur chaque carte.

### Règles du jeu (fioles)

Chaque fiole possède une couleur avec des règles spécifiques :

- **Jaune** : minimum 1 joueur  
- **Rouge** : minimum 2 joueurs  
- **Vert** : minimum 3 joueurs au total  
- **Bleu** : cas spécial (1 joueur peut battre ≥2 adversaires)

Ces règles rendent le problème fortement dépendant de la **coordination**.

## Description des stratégies proposées

Chaque stratégie est implémentée comme une fonction déterminant les fioles ciblées.

- **Stratégie random** :  
  Choix totalement aléatoire des fioles.

- **Stratégie coordination** :  
  Tous les joueurs ciblent la même fiole.

- **Stratégie fictitious play** :  
  Se base sur l'historique adverse pour prédire ses choix.

- **Stratégie regret matching** :  
  Utilise les regrets accumulés pour orienter les choix futurs.

- **Stratégie ε-regret matching** :  
  Combine exploration aléatoire et exploitation des regrets.

- **Stratégie greedy** :  
  Sélectionne les fioles avec le plus grand gain estimé (regret max).

- **Stratégie hybrid coordination-regret** :  
  Combine coordination et apprentissage par regret.

- **Stratégie hybrid fictitious-coordination** :  
  Combine imitation de l'adversaire et coordination.

- **Stratégie hybrid greedy-regret** :  
  Mélange stratégie agressive (greedy) et adaptative (regret).

## Description des résultats

Les stratégies ont été testées deux à deux sur toutes les cartes disponibles.  
Les résultats sont enregistrés dans un fichier CSV puis analysés à l'aide de graphes :

- winrate global
- score moyen
- winrate par carte
- heatmap des duels
- comparaison par couple de stratégies

### Winrate global

![Winrate global](graphs/winrate_global.png)

On observe que :

- **random** est la stratégie la plus performante (~73%)
- **regret** est également très efficace (~71%)
- **epsilon_regret** reste performante (~68%)

Contrairement à ce que l'on pourrait attendre, les stratégies basées sur l'apprentissage ne dominent pas complètement.

Cela montre que dans cet environnement, **l'imprévisibilité joue un rôle majeur**.

### Score moyen

![Score moyen](graphs/score_moyen_global.png)

Les résultats confirment que les stratégies ayant le meilleur winrate sont aussi celles qui obtiennent les meilleurs scores moyens.
La stratégie **random** obtient également de très bons scores moyens, ce qui renforce sa dominance globale.

## Analyse selon la carte

![Winrate par carte](graphs/winrate_par_carte.png)

- **random** est performante sur la majorité des cartes - stratégie robuste  
- **regret** et **epsilon_regret** restent compétitives.

La carte **mixed-map** est la plus complexe, car elle combine plusieurs types de fioles et nécessite à la fois coordination et adaptation.

Cela montre que certaines stratégies sont sensibles à l'environnement.

## Analyse des duels

![Heatmap](graphs/heatmap_duels.png)

- **random domine la majorité des stratégies**
- **regret et epsilon_regret sont également solides**
- **coordination et les stratégies hybrides sont souvent dominées**

Cette représentation permet de compléter les résultats globaux en montrant les forces et faiblesses spécifiques de chaque stratégie face à un adversaire donné.

La heatmap permet de visualiser directement qui bat qui.

## Comparaison de couples de stratégies

Conformément à l'énoncé, chaque couple de stratégies a été comparé.

### epsilon_regret vs random

![epsilon vs random](graphs_duels/epsilon_regret_vs_random.png)

random reste globalement supérieure grâce à son imprévisibilité.

### regret vs greedy

![regret vs greedy](graphs_duels/regret_vs_greedy.png)

regret surpasse greedy, montrant l'intérêt de l'apprentissage.

### coordination vs random

![coordination vs random](graphs_duels/coordination_vs_random.png)

coordination est trop rigide et se fait battre par une stratégie aléatoire.

## Observations détaillées

Ces résultats globaux et ces comparaisons nous permettent maintenant d'analyser plus finement le comportement de chaque stratégie.

### Analyse des performances stratégiques

- **Stratégie random :**
  - Très bonnes performances globales.
  - Imprévisible donc difficile à contrer.
  - Surprend par son efficacité.
  - Ne peut pas être exploitée par les stratégies adverses.
  - S'avère être la stratégie la plus robuste dans cet environnement.

- **Stratégie coordination :**
  - Très efficace sur les fioles nécessitant plusieurs joueurs (rouge, vert).
  - Peut échouer si la cible est contestée.

- **Stratégie fictitious play :**
  - Bonne adaptation face à des stratégies répétitives.
  - Performances variables selon la stabilité de l'adversaire.

- **Stratégie regret matching :**
  - Apprentissage progressif.
  - Performances solides sur le long terme.
  - S'adapte bien aux environnements dynamiques.

- **Stratégie ε-regret matching :**
  - Combine exploration et apprentissage.
  - Performante, mais moins efficace que random dans cet environnement instable.

- **Stratégie greedy :**
  - Très performante à court terme.
  - Peut manquer de diversité - vulnérable.

- **Stratégies hybrides :**
  - Certaines stratégies hybrides sont performantes, mais restent globalement moins efficaces que random dans ce contexte.

### Impact des cartes

- **Cartes simples (une seule couleur)** :
  - Les stratégies spécialisées dominent.

- **Carte mixed-map** :
  - Nécessite adaptation + coordination.
  - Favorise les stratégies les plus complètes.

## Conclusion générale

Le facteur clé de performance dépend ici fortement du comportement des adversaires.

Les résultats montrent que dans un environnement dynamique et compétitif, **l'imprévisibilité peut être plus efficace que l'apprentissage**.

La stratégie **random** obtient le meilleur winrate global (~73%), ce qui montre qu'une stratégie simple mais non déterministe peut surpasser des stratégies plus complexes.

Les stratégies basées sur :

- le **regret (learning)**  
- l'**exploration (epsilon)**  
- les **approches hybrides**

restent performantes, mais peuvent être pénalisées face à un adversaire imprévisible.

## Perspectives d'amélioration

- Ajustement dynamique de ε dans epsilon-regret  
- Introduction d'apprentissage par renforcement  
- Meilleure gestion de la coordination entre agents  
- Optimisation des déplacements  

## Conclusion finale

Ce projet nous a permis de mieux comprendre les mécanismes de prise de décision dans des systèmes multi-agents compétitifs.  
Il met en évidence que l'intelligence collective (coordination + adaptation) est plus efficace que les décisions individuelles isolées.

Ces résultats sont directement applicables à des domaines comme :

- robotique multi-agents  
- systèmes distribués  
- intelligence artificielle.