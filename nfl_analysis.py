import pandas as pd

# Load real NFL betting data straight from GitHub
url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

# First look at your data
print("=== Dataset Shape ===")
print(games.shape)
print("\n=== Column Names ===")
print(games.columns.tolist())
print("\n=== First 5 Rows ===")
print(games.head())


# Show specific columns that matter for betting analysis
cols = ["schedule_season", "schedule_week", "team_home", "team_away", 
        "score_home", "score_away", "spread_favorite", "team_favorite_id",
        "over_under_line", "favorite_covered", "over_under_result"]

print("\n=== Recent Games (2017 Season) ===")
recent = games[games["schedule_season"] == 2017][cols]
print(recent.head(20))

# Quick betting stats
print("\n=== How Often Does the Favorite Cover? ===")
print(games["favorite_covered"].value_counts())

print("\n=== Over vs Under Results ===")
print(games["over_under_result"].value_counts())

# Filter to just 2017 season
season = games[games["schedule_season"] == 2017]

print("\n=== 2017 Season Betting Analysis ===")
print("Total games:", len(season))

# How often did the favorite cover in 2017?
fav_covered = season["favorite_covered"].value_counts()
print("\nFavorite covered:", fav_covered)

# Home team win percentage
home_wins = season[season["score_home"] > season["score_away"]]
print("\nHome team won", len(home_wins), "out of", len(season), "games")
print("Home win %:", round(len(home_wins) / len(season) * 100, 2), "%")

# Average points scored
print("\nAvg home score:", round(season["score_home"].mean(), 1))
print("Avg away score:", round(season["score_away"].mean(), 1))

# Biggest blowouts
season_sorted = season.sort_values("score_difference", ascending=False)
print("\n=== Biggest Blowouts ===")
print(season_sorted[["team_home", "team_away", "score_home", "score_away", "score_difference"]].head(5))

# Which teams were best/worst against the spread in 2017?
print("\n=== Team ATS Records (2017) ===")

# Get home games where home team was the favorite
home_fav = season[season["home_favorite"] == 1]
home_dog = season[season["home_favorite"] == 0]

print("\nWhen home team is FAVORED:")
print("Favorite covers:", home_fav["favorite_covered"].value_counts().to_dict())

print("\nWhen home team is UNDERDOG:")
print("Favorite covers:", home_dog["favorite_covered"].value_counts().to_dict())

# Most common final score totals
print("\n=== Did Games Go Over or Under? ===")
over_pct = round(len(season[season["over_under_result"] == "over"]) / len(season) * 100, 1)
under_pct = round(len(season[season["over_under_result"] == "under"]) / len(season) * 100, 1)
print("Over:", over_pct, "%")
print("Under:", under_pct, "%")

