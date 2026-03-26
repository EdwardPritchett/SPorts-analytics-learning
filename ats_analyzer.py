import pandas as pd

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

def ats_report(year):
    season = games[games["schedule_season"] == year].copy()
    
    if len(season) == 0:
        print("No data for that year.")
        return
    
    # Get all teams that played that year
    teams = sorted(season["team_home"].unique())
    
    results = []
    
    for team in teams:
        home = season[season["team_home"] == team]
        away = season[season["team_away"] == team]
        
        # Wins and losses
        wins = len(home[home["score_home"] > home["score_away"]]) + \
               len(away[away["score_away"] > away["score_home"]])
        total = len(home) + len(away)
        losses = total - wins
        
        # ATS record: when this team was the favorite, did they cover?
        home_fav = home[(home["team_favorite_id"] == team) | 
                        (home["home_favorite"] == 1)]
        away_fav = away[(away["team_favorite_id"] == team)]
        
        # When this team was the underdog
        home_dog = home[home["home_favorite"] == 0]
        away_dog = away[away["team_favorite_id"] != team]
        
        # Over/under
        all_games = pd.concat([home, away])
        overs = len(all_games[all_games["over_under_result"] == "over"])
        unders = len(all_games[all_games["over_under_result"] == "under"])
        
        # Points per game
        pts_for = home["score_home"].sum() + away["score_away"].sum()
        ppg = round(pts_for / total, 1)
        
        results.append({
            "Team": team,
            "Record": f"{wins}-{losses}",
            "W": wins,
            "PPG": ppg,
            "Overs": overs,
            "Unders": unders,
            "O/U": f"{overs}-{unders}"
        })
    
    # Turn results into a DataFrame and sort by wins
    df = pd.DataFrame(results).sort_values("W", ascending=False)
    
    print(f"\n{'='*60}")
    print(f"  {year} NFL Season - Full Standings with Betting Stats")
    print(f"{'='*60}\n")
    print(df[["Team", "Record", "PPG", "O/U"]].to_string(index=False))

# Run it
year = int(input("Enter season year (1979-2017): "))
ats_report(year)