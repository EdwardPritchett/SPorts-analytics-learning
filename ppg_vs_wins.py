import pandas as pd
import matplotlib.pyplot as plt

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

season = games[games["schedule_season"] == 2017]
teams = sorted(season["team_home"].unique())

results = []
for team in teams:
    home = season[season["team_home"] == team]
    away = season[season["team_away"] == team]
    wins = len(home[home["score_home"] > home["score_away"]]) + \
           len(away[away["score_away"] > away["score_home"]])
    total = len(home) + len(away)
    pts_for = home["score_home"].sum() + away["score_away"].sum()
    pts_against = home["score_away"].sum() + away["score_home"].sum()
    ppg = round(pts_for / total, 1)
    papg = round(pts_against / total, 1)
    results.append({"Team": team, "Wins": wins, "PPG": ppg, "PAPG": papg,
                    "Diff": round(ppg - papg, 1)})

df = pd.DataFrame(results)

fig, ax = plt.subplots(figsize=(12, 8))

# Color by point differential
colors = df["Diff"]
scatter = ax.scatter(df["PPG"], df["Wins"], c=colors, cmap="RdYlGn", 
                     s=150, edgecolors="black", linewidth=0.5, zorder=5)

# Label each dot with team name
for _, row in df.iterrows():
    ax.annotate(row["Team"].split()[-1], (row["PPG"], row["Wins"]),
                fontsize=7, ha="center", va="bottom", 
                xytext=(0, 8), textcoords="offset points")

ax.set_xlabel("Points Per Game", fontsize=14)
ax.set_ylabel("Wins", fontsize=14)
ax.set_title("2017 NFL: Points Per Game vs Wins", fontsize=18, fontweight="bold")
ax.axhline(y=8, color="gray", linestyle="--", alpha=0.3)

plt.colorbar(scatter, label="Point Differential Per Game")
plt.tight_layout()
plt.savefig("ppg_vs_wins.png", dpi=150)
print("Chart saved as ppg_vs_wins.png")
plt.show()