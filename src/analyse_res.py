import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# 0. Dossiers de sortie
# -----------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
docs_dir = os.path.join(base_dir, "docs")
graphs_dir = os.path.join(docs_dir, "graphs")
globaux_dir = os.path.join(graphs_dir, "globaux")
par_carte_dir = os.path.join(graphs_dir, "par_carte")
heatmaps_dir = os.path.join(graphs_dir, "heatmaps")
duels_dir = os.path.join(graphs_dir, "duels")

os.makedirs(globaux_dir, exist_ok=True)
os.makedirs(par_carte_dir, exist_ok=True)
os.makedirs(heatmaps_dir, exist_ok=True)
os.makedirs(duels_dir, exist_ok=True)

# -----------------------------
# 1. Lecture du csv
# -----------------------------
csv_path = os.path.join(base_dir, "results.csv")
df = pd.read_csv(csv_path)

# -----------------------------
# 2. Détermination du gagnant
# -----------------------------
def get_winner(row):
    if row["score0"] > row["score1"]:
        return row["strat0"]
    elif row["score1"] > row["score0"]:
        return row["strat1"]
    else:
        return "egalite"

df["winner"] = df.apply(get_winner, axis=1)

# toutes les stratégies sauf egalite
strategies = sorted(set(df["strat0"]).union(set(df["strat1"])))
maps = sorted(df["map"].unique())

# -----------------------------
# 3. Winrate global par stratégie
# -----------------------------
wins = {s: 0 for s in strategies}
matches = {s: 0 for s in strategies}

for _, row in df.iterrows():
    s0 = row["strat0"]
    s1 = row["strat1"]
    matches[s0] += 1
    matches[s1] += 1

    if row["winner"] == s0:
        wins[s0] += 1
    elif row["winner"] == s1:
        wins[s1] += 1

winrates = {s: wins[s] / matches[s] if matches[s] > 0 else 0 for s in strategies}

winrate_df = pd.DataFrame({
    "strategy": list(winrates.keys()),
    "winrate": list(winrates.values())
}).sort_values("winrate", ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(winrate_df["strategy"], winrate_df["winrate"])
plt.title("Winrate global par stratégie")
plt.ylabel("Winrate")
plt.xlabel("Stratégie")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(globaux_dir, "winrate_global.png"))
plt.close()

# -----------------------------
# 4. Score moyen global par stratégie
# -----------------------------
score_data = []

for strat in strategies:
    scores_as_0 = df[df["strat0"] == strat]["score0"]
    scores_as_1 = df[df["strat1"] == strat]["score1"]
    all_scores = pd.concat([scores_as_0, scores_as_1])
    score_data.append({
        "strategy": strat,
        "avg_score": all_scores.mean()
    })

score_df = pd.DataFrame(score_data).sort_values("avg_score", ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(score_df["strategy"], score_df["avg_score"])
plt.title("Score moyen global par stratégie")
plt.ylabel("Score moyen")
plt.xlabel("Stratégie")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(globaux_dir, "score_moyen_global.png"))
plt.close()

# -----------------------------
# 5. Winrate par carte
# -----------------------------
winrate_by_map = pd.DataFrame(index=maps, columns=strategies)

for m in maps:
    df_map = df[df["map"] == m]

    for strat in strategies:
        wins_s = 0
        matches_s = 0

        for _, row in df_map.iterrows():
            if row["strat0"] == strat:
                matches_s += 1
                if row["winner"] == strat:
                    wins_s += 1

            if row["strat1"] == strat:
                matches_s += 1
                if row["winner"] == strat:
                    wins_s += 1

        winrate_by_map.loc[m, strat] = wins_s / matches_s if matches_s > 0 else 0

winrate_by_map = winrate_by_map.astype(float)

# graphe global toutes les stratégies selon la carte
plt.figure(figsize=(12, 6))
for strat in strategies:
    plt.plot(winrate_by_map.index, winrate_by_map[strat], marker="o", label=strat)

plt.title("Winrate des stratégies selon la carte")
plt.ylabel("Winrate")
plt.xlabel("Carte")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(par_carte_dir, "winrate_par_carte.png"))
plt.close()

# un graphe par stratégie selon les cartes
for strat in strategies:
    plt.figure(figsize=(8, 4))
    plt.plot(winrate_by_map.index, winrate_by_map[strat], marker="o")
    plt.title(f"Winrate de {strat} selon la carte")
    plt.ylabel("Winrate")
    plt.xlabel("Carte")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(par_carte_dir, f"{strat}_par_carte.png"))
    plt.close()

# -----------------------------
# 6. Heatmap des duels
# -----------------------------
heatmap = pd.DataFrame(0.0, index=strategies, columns=strategies)

for s0 in strategies:
    for s1 in strategies:
        subset = df[(df["strat0"] == s0) & (df["strat1"] == s1)]

        if len(subset) > 0:
            wins_0 = (subset["winner"] == s0).sum()
            heatmap.loc[s0, s1] = wins_0 / len(subset)
        else:
            heatmap.loc[s0, s1] = np.nan

plt.figure(figsize=(10, 8))
plt.imshow(heatmap, aspect="auto")
plt.colorbar(label="Taux de victoire de la stratégie en ligne")
plt.xticks(range(len(strategies)), strategies, rotation=45, ha="right")
plt.yticks(range(len(strategies)), strategies)
plt.title("Heatmap des duels stratégie vs stratégie")
plt.xlabel("Stratégie adverse")
plt.ylabel("Stratégie en ligne")

for i in range(len(strategies)):
    for j in range(len(strategies)):
        value = heatmap.iloc[i, j]
        if not np.isnan(value):
            plt.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(heatmaps_dir, "heatmap_duels.png"))
plt.close()

# -----------------------------
# 7. Graphes par couple de stratégies
# -----------------------------
for i, s0 in enumerate(strategies):
    for j, s1 in enumerate(strategies):
        if i >= j:
            continue

        subset_01 = df[(df["strat0"] == s0) & (df["strat1"] == s1)]
        subset_10 = df[(df["strat0"] == s1) & (df["strat1"] == s0)]

        total_matches = len(subset_01) + len(subset_10)
        if total_matches == 0:
            continue

        wins_s0 = ((subset_01["winner"] == s0).sum() +
                   (subset_10["winner"] == s0).sum())
        wins_s1 = ((subset_01["winner"] == s1).sum() +
                   (subset_10["winner"] == s1).sum())

        winrate_0 = wins_s0 / total_matches
        winrate_1 = wins_s1 / total_matches

        plt.figure(figsize=(6, 4))
        plt.bar([s0, s1], [winrate_0, winrate_1])
        plt.title(f"{s0} vs {s1}")
        plt.ylabel("Winrate")
        plt.ylim(0, 1)

        plt.text(0, winrate_0 + 0.02, f"{winrate_0:.2f}", ha="center")
        plt.text(1, winrate_1 + 0.02, f"{winrate_1:.2f}", ha="center")

        plt.tight_layout()
        plt.savefig(os.path.join(duels_dir, f"{s0}_vs_{s1}.png"))
        plt.close()

print("Tous les graphes ont été sauvegardés dans docs/graphs/")