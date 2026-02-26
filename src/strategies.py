import random
import numpy as np

#strategie aleatoire uniforme
def strategy_random_uniform(items):
    """
    chaque joueur choisit une fiole au hasard parmi les fioles disponibles
    """
    fioles_dispos = items #liste des fioles disponibles
    return [random.choice(fioles_dispos) for _ in range(len(items))]


