import pandas as pd

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

def team_report(team_name, year):
    # Games where this team played (home or away)
    season = games[games["schedule_season"] == year]
    home = season[season["team_home"] == team_name]
    away = season[season["team_away"] == team_name]
    
    total_games = len(home) + len(away)
    
    if total_games == 0:
        print("No games found. Check the team name and year.")
        return
    
    # Win/Loss record
    home_wins = len(home[home["score_home"] > home["score_away"]])
    away_wins = len(away[away["score_away"] > away["score_home"]])
    total_wins = home_wins + away_wins
    total_losses = total_games - total_wins
    
    # Points
    home_pts_for = home["score_home"].sum()
    home_pts_against = home["score_away"].sum()
    away_pts_for = away["score_away"].sum()
    away_pts_against = away["score_home"].sum()
    total_pts_for = home_pts_for + away_pts_for
    total_pts_against = home_pts_against + away_pts_against
    
    # Average spread when favored
    print(f"\n{'='*40}")
    print(f"  {team_name} - {year} Season Report")
    print(f"{'='*40}")
    print(f"  Record: {total_wins}-{total_losses}")
    print(f"  Home: {home_wins}-{len(home) - home_wins}")
    print(f"  Away: {away_wins}-{len(away) - away_wins}")
    print(f"  Points For: {total_pts_for} ({round(total_pts_for/total_games, 1)} ppg)")
    print(f"  Points Against: {total_pts_against} ({round(total_pts_against/total_games, 1)} ppg)")
    print(f"  Point Diff: {total_pts_for - total_pts_against}")
    print(f"{'='*40}\n")

# Let the user look up any team
print("=== NFL Team Season Lookup ===\n")

# Show available teams for the year
year = int(input("Enter season year (1967-2017): "))
teams_that_year = sorted(games[games["schedule_season"] == year]["team_home"].unique())
print("\nAvailable teams:")
for i, team in enumerate(teams_that_year):
    print(f"  {i+1}. {team}")

team = input("\nEnter exact team name from list above: ")
team_report(team, year)
