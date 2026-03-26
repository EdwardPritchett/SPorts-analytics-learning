import pandas as pd
import matplotlib.pyplot as plt

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

# Get 2017 season
season = games[games["schedule_season"] == 2017]

# Build team win totals
teams = sorted(season["team_home"].unique())
results = []

for team in teams:
    home = season[season["team_home"] == team]
    away = season[season["team_away"] == team]
    wins = len(home[home["score_home"] > home["score_away"]]) + \
           len(away[away["score_away"] > away["score_home"]])
    total = len(home) + len(away)
    ppg = round((home["score_home"].sum() + away["score_away"].sum()) / total, 1)
    results.append({"Team": team, "Wins": wins, "PPG": ppg})

df = pd.DataFrame(results).sort_values("Wins", ascending=True)

# CHART 1: Horizontal bar chart of wins
fig, ax = plt.subplots(figsize=(10, 12))

colors = ["#d32f2f" if w < 6 else "#ff9800" if w < 10 else "#2e7d32" for w in df["Wins"]]

ax.barh(df["Team"], df["Wins"], color=colors)
ax.set_xlabel("Wins", fontsize=14)
ax.set_title("2017 NFL Season - Wins by Team", fontsize=18, fontweight="bold")
ax.axvline(x=8, color="gray", linestyle="--", alpha=0.5, label=".500 line")
ax.legend()

plt.tight_layout()
plt.savefig("nfl_wins_2017.png", dpi=150)
print("Chart saved as nfl_wins_2017.png")
plt.show()


