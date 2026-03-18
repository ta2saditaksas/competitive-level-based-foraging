import random
import numpy as np

#strategie aleatoire uniforme
def strategy_random_uniform(items):
    """
    chaque joueur choisit une fiole au hasard parmi les fioles disponibles
    """
    fioles_dispos = items #liste des fioles disponibles
    return [random.choice(fioles_dispos) for _ in range(len(items))]


#strategie fictitious play (apprentissage a partir de l historique de l equipe 0
def strategy_fictitious_play(items, history_team_0):
    """
    l equipe 1 choisit les fioles bases sur les choix passes de equipe 0
    """
    fiole_cpt = {fiole: history_team_0.count(fiole) for fiole in items}
    fiole_plus_choisie = max(fiole_cpt, key=fiole_cpt.get)
    return [fiole_plus_choisie] * len(items) #ici tous les joueurs choisisent la meme fiole

#strategie stationnaire tetue
def strategy_stationary(tetue_allocation):
    """
    on attribue des fioles fixes pour chaque joueur
    """
    return tetue_allocation

#strategie aleatoire avec coordinations
def strategy_random_with_coordination(items):
    """
    tous les joueurs d une meme equipe choisissent la meme fiole tiree de maniere aleatoire a chaque episode
    """
    chosen_flask = random.choice(items)
    return [chosen_flask] * len(items)

#strategie aleatoire expert
def strategy_aléatoire_expert(items, expert_allocations):
    """
    on attribue une fiole parmi un ensemble pedefini de configurations
    """
    return random.choice(expert_allocations)

#strategie de regret matching
def strategy_regret_matching(items, nb_players, regrets):
    """
    on choisit une fiole pour chaque joueur en se basant sur les regrets accumules dans les ep prec
    """
    nb_flasks = len(items) #nombre total de fioles
    positive_regrets = [max(0, r) for r in regrets] #on garde seulement les regrets positifs cad les erreurs utiles
    total = sum(positive_regrets) #somme des regrets pour faire un tirage pondere
    chosen_indices = [] #indices de fioles choisis par les joueurs

    #on choisit une fiole pour chaque joueur
    for _ in range(nb_players):
        if total == 0: #si aucun regret on choisit au hasard
            idx = random.randint(0, nb_flasks - 1)
        else: #sinon on fait un tirage aleatoire proportionnel aux regrets
            r = random.random() * total
            cumul = 0.0
            idx = nb_flasks - 1  #valeur par defaut
            for i in range(nb_flasks): #on parcourt les fioles
                cumul += positive_regrets[i] 
                if cumul >= r: #des qu on depasse r on choisit cette fiole
                    idx = i
                    break
        chosen_indices.append(idx) #on ajoute l indice choisi
    #on convertit les indices en fioles
    chosen_flasks = [items[i] for i in chosen_indices]

    #on retourne les fioles choisies et les indices qu on utilisera pour maj
    return chosen_flasks, chosen_indices
