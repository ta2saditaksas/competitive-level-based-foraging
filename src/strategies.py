import random
import numpy as np

#strategie aleatoire uniforme
def strategy_random_uniform(items):
    """
    chaque joueur choisit une fiole au hasard parmi les fioles disponibles
    """
    fioles_dispos = items #liste des fioles disponibles
    return [random.choice(fioles_dispos) for _ in range(len(items))]


#strategie fictitious play (apprentissage à partir de l'historique de l'équipe 0) ---
def strategy_fictitious_play(items, history_team_0):
    """
    l equipe 1 choisit les fioles bases sur les choix passes de equipe 0
    """
    fiole_cpt = {fiole: history_team_0.count(fiole) for fiole in items}
    fiole_plus_choisie = max(fiole_cpt, key=fiole_cpt.get)
    return [fiole_plus_choisie] * len(items) #ici tous les joueurs choisisent la meme fiole