import pandas as pd
import matplotlib.pyplot as plt

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

# Track over/under percentages by year
years = range(1979, 2018)
over_pcts = []

for year in years:
    season = games[games["schedule_season"] == year]
    total = len(season[season["over_under_result"].isin(["over", "under"])])
    if total > 0:
        overs = len(season[season["over_under_result"] == "over"])
        over_pcts.append(round(overs / total * 100, 1))
    else:
        over_pcts.append(0)

# Line chart showing the trend over decades
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(years, over_pcts, color="#1565C0", linewidth=2, marker="o", markersize=4)
ax.axhline(y=50, color="red", linestyle="--", alpha=0.7, label="50% line")
ax.fill_between(years, over_pcts, 50, where=[p > 50 for p in over_pcts], 
                alpha=0.2, color="green", label="Over-heavy seasons")
ax.fill_between(years, over_pcts, 50, where=[p < 50 for p in over_pcts], 
                alpha=0.2, color="red", label="Under-heavy seasons")

ax.set_xlabel("Season", fontsize=14)
ax.set_ylabel("Over %", fontsize=14)
ax.set_title("NFL Over/Under Hit Rate (1979-2017)", fontsize=18, fontweight="bold")
ax.legend(fontsize=12)
ax.set_ylim(35, 65)

plt.tight_layout()
plt.savefig("over_under_trend.png", dpi=150)
print("Chart saved as over_under_trend.png")
plt.show()
