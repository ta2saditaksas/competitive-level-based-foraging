# -*- coding: utf-8 -*-

# Nicolas, 2026-02-09
from __future__ import absolute_import, print_function, unicode_literals

import random
import numpy as np
import sys
from itertools import chain

import pygame

from pySpriteWorld.gameclass import Game, check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme
from strategies import (strategy_random_uniform,strategy_fictitious_play,strategy_random_with_coordination,strategy_regret_matching,update_regrets,strategy_hybrid_coordination_regret,strategy_hybrid_fictitious_coordination,strategy_aleatoire_expert)

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player, game
    name = _boardname if _boardname is not None else 'mixed-map'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
    game.mainiteration()
    player = game.player

def main():
    init()

    # -------------------------------
    # Initialisation
    # -------------------------------

    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols  # plateau carré
    lMin = 2
    lMax = nb_lignes - 2
    cMin = 2
    cMax = nb_cols - 2

    players = [o for o in game.layers['joueur']]
    nb_players = len(players)

    items = [o for o in game.layers["ramassable"]]  # fioles
    nb_fioles = len(items)

    nb_episodes = 20 

    # -------------------------------
    # Fonctions pour récupérer les coordonnées
    # -------------------------------

    def item_states(items):
        return [o.get_rowcol() for o in items]

    def player_states(players):
        return [p.get_rowcol() for p in players]

    # -------------------------------
    # Rapport carte
    # -------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs:', nb_players)
    print("fioles:", nb_fioles)
    print("lignes:", nb_lignes)
    print("colonnes:", nb_cols)
    print("-------------------------------------------")

    # -------------------------------
    # Équipes (2 x 8 joueurs)
    # -------------------------------

    team = [[], []]
    for o in players:
        (x, y) = o.get_rowcol()
        if x == 2:  # team 0 en haut
            team[0].append(o)
        elif x == 18:  # team 1 en bas
            team[1].append(o)

    assert len(team[0]) == len(team[1])
    nb_players_team = int(nb_players / 2)

    init_states = [[], []]
    init_states[0] = player_states(team[0])
    init_states[1] = player_states(team[1])

    # -------------------------------
    # Positions autour + positions légales
    # -------------------------------

    def around_pos(pos):
        x, y = pos
        return [(x-1,y-1),(x-1,y),(x-1,y+1),
                (x,y-1),(x,y+1),
                (x+1,y-1),(x+1,y),(x+1,y+1)]

    def legal_position(pos):
        row, col = pos
        return ((pos not in item_states(items)) and
                (pos not in player_states(players)) and
                row > lMin and row < lMax-1 and
                col >= cMin and col < cMax)

    def around_pos_free(pos):
        return [p for p in around_pos(pos) if legal_position(p)]

    def busy(pos):
        return around_pos_free(pos) == []

    def players_around_item(f):
        """
        :param f: objet fiole
        :return: [nb_team0, nb_team1]
        """
        are_here = [0, 0]
        pos = f.get_rowcol()
        for i in [0, 1]:
            for j in team[i]:
                if j.get_rowcol() in around_pos(pos):
                    are_here[i] += 1
        return are_here

    # -------------------------------
    # Couleur d'une fiole via tileid
    # -------------------------------
    # IMPORTANT :
    # tileid = (row, col) dans la spritesheet (16 colonnes).
    # On a vérifié via les .json:
    # blue-map => gid 293 => tileid (18,4) => donc (18,4) = "blue"
    #
    # Hypothèse cohérente sur les autres maps :
    # gid 306 -> (19,1) jaune ; gid 277 -> (17,4) rouge ; gid 338 -> (21,1) vert.
    #
    # Si jamais ça ne colle pas : tu peux afficher f.tileid sur chaque map et ajuster.

    TILEID_TO_COLOR = {
        (18, 4): "blue",
        (19, 1): "yellow",
        (17, 4): "red",
        (21, 1): "green",
    }

    def flask_color(flask):
        if flask.tileid in TILEID_TO_COLOR:
            return TILEID_TO_COLOR[flask.tileid]
        raise ValueError(f"tileid fiole inconnu: {flask.tileid} (ajoute-le dans TILEID_TO_COLOR)")

    # -------------------------------
    # Règles de victoire sur une fiole
    # -------------------------------

    def winner_for_flask(color, c0, c1):
        # égalité => personne ne collecte
        if c0 == c1:
            return None

        if color == "yellow":
            # min 1 joueur de la même équipe
            if c0 >= 1 and c1 >= 1:
                return 0 if c0 > c1 else 1
            if c0 >= 1:
                return 0
            if c1 >= 1:
                return 1
            return None

        if color == "red":
            # min 2 joueurs de la même équipe
            if c0 >= 2 and c1 >= 2:
                return 0 if c0 > c1 else 1
            if c0 >= 2:
                return 0
            if c1 >= 2:
                return 1
            return None

        if color == "green":
            # min 3 joueurs au total
            if c0 + c1 < 3:
                return None
            return 0 if c0 > c1 else 1

        if color == "blue":
            # Exception "solo" :
            # si un joueur est seul (==1) et l'autre équipe a >=2, le solo gagne.
            if c0 == 1 and c1 >= 2:
                return 0
            if c1 == 1 and c0 >= 2:
                return 1

            # sinon comme rouge
            if c0 >= 2 and c1 >= 2:
                return 0 if c0 > c1 else 1
            if c0 >= 2:
                return 0
            if c1 >= 2:
                return 1
            return None

        raise ValueError("Couleur inconnue: " + str(color))

    # -------------------------------
    # Strategie aleatoire + jeu multi-épisodes
    # -------------------------------

    score_total = [0, 0]

    #historique des choix de chaque equipe
    history_team_0 = []
    history_team_1 = []
    #regrets de chaque equipe (un regret par fiole)
    regrets_team_0 = [0] * len(items)
    regrets_team_1 = [0] * len(items)
    #choix de strategie pour chaque equipe
    strategy_team_0 = "random"
    strategy_team_1 = "coordination"

    for e in range(nb_episodes):
        # équité : on inverse la priorité à chaque épisode
        priority = [0, 1] if (e % 2 == 0) else [1, 0]
        print("\n===== EPISODE", e, "priority =", priority, "=====")

        #on garde les indices des fioles choisies pendant cet episode
        chosen_indices_teams = [[], []]

        for t in priority:
            print("Team", t)
            path = []
            choix_fiole = []
            choix_pos = []

            # -------------------------------
            # choix de la strategie selon l equipe
            # -------------------------------
            if t == 0:
                if strategy_team_0 == "random":
                    choix_fiole = strategy_random_uniform(items, nb_players_team)

                elif strategy_team_0 == "coordination":
                    choix_fiole = strategy_random_with_coordination(items, nb_players_team)

                elif strategy_team_0 == "fictitious":
                    choix_fiole = strategy_fictitious_play(items, nb_players_team, history_team_1)

                elif strategy_team_0 == "regret":
                    choix_fiole, chosen_idx = strategy_regret_matching(items, nb_players_team, regrets_team_0)
                    chosen_indices_teams[0] = chosen_idx

                elif strategy_team_0 == "hybrid_regret":
                    choix_fiole = strategy_hybrid_coordination_regret(items, nb_players_team, regrets_team_0)

                elif strategy_team_0 == "hybrid_fictitious":
                    choix_fiole = strategy_hybrid_fictitious_coordination(items, nb_players_team, history_team_1)

                else:
                    choix_fiole = strategy_random_uniform(items, nb_players_team)

            else:
                if strategy_team_1 == "random":
                    choix_fiole = strategy_random_uniform(items, nb_players_team)

                elif strategy_team_1 == "coordination":
                    choix_fiole = strategy_random_with_coordination(items, nb_players_team)

                elif strategy_team_1 == "fictitious":
                    choix_fiole = strategy_fictitious_play(items, nb_players_team, history_team_0)

                elif strategy_team_1 == "regret":
                    choix_fiole, chosen_idx = strategy_regret_matching(items, nb_players_team, regrets_team_1)
                    chosen_indices_teams[1] = chosen_idx

                elif strategy_team_1 == "hybrid_regret":
                    choix_fiole = strategy_hybrid_coordination_regret(items, nb_players_team, regrets_team_1)

                elif strategy_team_1 == "hybrid_fictitious":
                    choix_fiole = strategy_hybrid_fictitious_coordination(items, nb_players_team, history_team_0)

                else:
                    choix_fiole = strategy_random_uniform(items, nb_players_team)

            
            # -------------------------------
            # placement + deplacement
            # -------------------------------
            for p in range(nb_players_team):
                f = choix_fiole[p]

                # si plus de place autour, on cherche une autre fiole
                essais = 0
                while busy(f.get_rowcol()) and essais < len(items):
                    f = random.choice(items)
                    essais += 1
                # si la strategie n a pas fourni les indices, on les reconstruit
                if len(chosen_indices_teams[t]) < nb_players_team:
                    chosen_indices_teams[t].append(items.index(f))
                else:
                    chosen_indices_teams[t][p] = items.index(f)

                free_pos = around_pos_free(f.get_rowcol())
                if free_pos:
                    chosen_pos = random.choice(free_pos)
                else:
                    chosen_pos = team[t][p].get_rowcol()

                choix_pos.append(chosen_pos)

                pos_player = team[t][p].get_rowcol()
                print("Player", p, "start", pos_player, "-> fiole", f.get_rowcol(), "pos", chosen_pos)
                
                g = np.ones((nb_lignes, nb_cols), dtype=bool)
                for i in range(nb_lignes):
                    g[0][i] = False
                    g[1][i] = False
                    g[nb_lignes - 1][i] = False
                    g[nb_lignes - 2][i] = False
                    g[i][0] = False
                    g[i][1] = False
                    g[i][nb_lignes - 1] = False
                    g[i][nb_lignes - 2] = False

                prob = ProblemeGrid2D(pos_player, chosen_pos, g, 'manhattan')
                path_player = probleme.astar(prob, verbose=False)

                for step in path_player:
                    row, col = step
                    team[t][p].set_rowcol(row, col)
                    game.mainiteration()

            # -------------------------------
        # Calcul du score de l'épisode
        # -------------------------------
        score_episode = [0, 0]
        counts_team0 = []
        counts_team1 = []

        print("\n--- Comptage autour des fioles ---")
        for f in items:
            c0, c1 = players_around_item(f)
            counts_team0.append(c0)
            counts_team1.append(c1)

            col = flask_color(f)
            w = winner_for_flask(col, c0, c1)

            print("Fiole", f.get_rowcol(), "tileid", f.tileid, "color", col, "counts", (c0, c1), "winner", w)

            if w == 0:
                score_episode[0] += 1
            elif w == 1:
                score_episode[1] += 1

        # mise a jour du score total
        score_total[0] += score_episode[0]
        score_total[1] += score_episode[1]

        print("Score épisode :", score_episode)
        print("Score total   :", score_total)

        # mise a jour de l historique
        history_team_0.extend([items[idx] for idx in chosen_indices_teams[0]])
        history_team_1.extend([items[idx] for idx in chosen_indices_teams[1]])

        # mise a jour des regrets
        if strategy_team_0 in ["regret", "hybrid_regret"]:
            regrets_team_0 = update_regrets(
                0, chosen_indices_teams[0], counts_team0, counts_team1,
                items, regrets_team_0, flask_color, winner_for_flask
            )

        if strategy_team_1 in ["regret", "hybrid_regret"]:
            regrets_team_1 = update_regrets(
                1, chosen_indices_teams[1], counts_team0, counts_team1,
                items, regrets_team_1, flask_color, winner_for_flask
            )

        # -------------------------------
        # Remettre les joueurs à leurs positions initiales
        # -------------------------------
        for i in [0, 1]:
            j = 0
            for p in team[i]:
                x, y = init_states[i][j]
                p.set_rowcol(x, y)
                j += 1
        game.mainiteration()

    # gagnant final
    print("\n===== FIN PARTIE =====")
    if score_total[0] > score_total[1]:
        print("Equipe 0 gagne !")
    elif score_total[1] > score_total[0]:
        print("Equipe 1 gagne !")
    else:
        print("Egalité !")

    pygame.quit()

   

if __name__ == '__main__':
    main()
    


