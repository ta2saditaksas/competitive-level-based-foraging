import random
import numpy as np

#strategie aleatoire uniforme
def strategy_random_uniform(items, nb_players):
    """
    chaque joueur choisit une fiole au hasard parmi les fioles disponibles
    """
    fioles_dispos = items #liste des fioles disponibles
    return [random.choice(fioles_dispos) for _ in range(nb_players)]


#strategie fictitious play (apprentissage a partir de l historique de l equipe 0
def strategy_fictitious_play(items, nb_players, history_team_0):
    """
    l equipe 1 choisit les fioles bases sur les choix passes de equipe 0
    """
    if not history_team_0:
        return strategy_random_uniform(items, nb_players)

    fiole_cpt = {fiole: history_team_0.count(fiole) for fiole in items}
    fiole_plus_choisie = max(fiole_cpt, key=fiole_cpt.get)
    return [fiole_plus_choisie] * nb_players

#strategie stationnaire tetue
def strategy_stationary(tetue_allocation):
    """
    on attribue des fioles fixes pour chaque joueur
    """
    return tetue_allocation

#strategie aleatoire avec coordinations
def strategy_random_with_coordination(items, nb_players):
    """
    tous les joueurs d une meme equipe choisissent la meme fiole tiree de maniere aleatoire a chaque episode
    """
    chosen_flask = random.choice(items)
    return [chosen_flask] * nb_players

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

#maj des regrets
def update_regrets(team_id, chosen_indices, counts_team0, counts_team1, items, regrets, flask_color, winner_for_flask):
    """
    maj des regrets apres un episode, pour chaque joueur on regarde si une autre fiole aurait pu etre meilleure
    """
    nb_flasks = len(items)
    for chosen_idx in chosen_indices: #on parcourt tous les choix fait par les joueurs de l equipe
        #gain reel obtenu avec la fiole choisie
        color_reel = flask_color(items[chosen_idx]) #on recupere la couleur de la fiole
        winner_reel = winner_for_flask(color_reel, counts_team0[chosen_idx], counts_team1[chosen_idx]) #qui a gagne cette fiole avec les jouers autour
        gain_reel = 1 if winner_reel == team_id else 0 #1 si mon equipe gagne la fiole, 0 sino n
        #on teste toutes les autres fioles
        for alt_idx in range(nb_flasks): #on copie les comptes actuels
            hypo_c0 = counts_team0[:]
            hypo_c1 = counts_team1[:]

            #on simule le deplacement du joueur vers une autre fiole
            if team_id == 0:
                hypo_c0[chosen_idx] -= 1 #on l enlve de sa fiole actuel
                hypo_c0[alt_idx] += 1 #on l ajoute a une autre
            else:
                hypo_c1[chosen_idx] -= 1
                hypo_c1[alt_idx] += 1

            color_alt = flask_color(items[alt_idx]) #on recup la couleur de la fiole alternative
            winner_alt = winner_for_flask(color_alt, hypo_c0[alt_idx], hypo_c1[alt_idx]) #qui aurait gagne avec cette nouvelle situation
            gain_alt = 1 if winner_alt == team_id else 0 #si mon equipe aurait gagne gain+1 sinon 0
            #si une autre fiole aurait ete meilleure, on augmente le regret
            regrets[alt_idx] += max(0, gain_alt - gain_reel)

    return regrets