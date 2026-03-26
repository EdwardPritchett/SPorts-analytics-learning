import pandas as pd

# Dataset 1: Team offensive stats
offense = pd.DataFrame({
    "Team": ["KC", "BUF", "BAL", "DET", "DAL", "CIN", "LAR"],
    "PPG": [27.2, 28.4, 25.1, 26.8, 22.1, 18.1, 28.9],
    "YPG": [365, 371, 345, 358, 320, 301, 370],
    "Turnovers": [12, 15, 10, 18, 20, 16, 14]
})

# Dataset 2: Team defensive stats
defense = pd.DataFrame({
    "Team": ["KC", "BUF", "BAL", "DET", "DAL", "CIN", "LAR"],
    "PAPG": [21.5, 23.1, 18.4, 22.3, 25.7, 24.2, 24.8],
    "Sacks": [45, 52, 48, 38, 41, 35, 44],
    "Takeaways": [22, 18, 25, 15, 12, 19, 16]
})

# Dataset 3: Betting results
betting = pd.DataFrame({
    "Team": ["KC", "BUF", "BAL", "DET", "DAL", "CIN", "LAR"],
    "Wins": [11, 13, 13, 12, 7, 9, 10],
    "ATS_Wins": [9, 10, 11, 8, 5, 7, 8],
    "ATS_Losses": [8, 7, 6, 9, 12, 10, 9]
})

# MERGE them all together on the "Team" column
team_stats = offense.merge(defense, on="Team").merge(betting, on="Team")

print("=== Combined Team Stats ===\n")
print(team_stats)

# Now you can calculate things using columns from BOTH datasets
team_stats["Point_Diff"] = round(team_stats["PPG"] - team_stats["PAPG"], 1)
team_stats["Turnover_Margin"] = team_stats["Takeaways"] - team_stats["Turnovers"]
team_stats["ATS_Pct"] = round(team_stats["ATS_Wins"] / 
    (team_stats["ATS_Wins"] + team_stats["ATS_Losses"]) * 100, 1)

print("\n=== Teams Ranked by ATS Win % ===\n")
ranked = team_stats.sort_values("ATS_Pct", ascending=False)
print(ranked[["Team", "Wins", "Point_Diff", "Turnover_Margin", "ATS_Pct"]].to_string(index=False))

# Find correlations — what stats predict ATS success?
print("\n=== What Predicts Covering the Spread? ===")
print("Correlation with ATS Win %:")
for col in ["PPG", "PAPG", "Point_Diff", "Turnover_Margin", "Sacks", "YPG"]:
    corr = round(team_stats["ATS_Pct"].corr(team_stats[col]), 3)
    direction = "+" if corr > 0 else ""
    print(f"  {col}: {direction}{corr}")