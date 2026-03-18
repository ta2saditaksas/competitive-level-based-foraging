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
