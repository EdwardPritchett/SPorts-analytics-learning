import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    
    # Over/under record
    all_games = pd.concat([home, away])
    overs = len(all_games[all_games["over_under_result"] == "over"])
    unders = len(all_games[all_games["over_under_result"] == "under"])
    
    results.append({
        "Team": team, "Wins": wins, "Losses": total - wins,
        "PPG": ppg, "PAPG": papg, "Diff": round(ppg - papg, 1),
        "Overs": overs, "Unders": unders,
        "Over_Pct": round(overs / (overs + unders) * 100, 1) if (overs + unders) > 0 else 0
    })

df = pd.DataFrame(results)

# CHART 1: Interactive scatter — hover over any team for full stats
fig1 = px.scatter(df, x="PPG", y="Wins", color="Diff", size="PPG",
                  hover_name="Team",
                  hover_data={"PPG": True, "PAPG": True, "Diff": True, 
                              "Overs": True, "Unders": True},
                  color_continuous_scale="RdYlGn",
                  title="2017 NFL: Points Per Game vs Wins (Hover for Details)")

fig1.add_hline(y=8, line_dash="dash", line_color="gray", opacity=0.5,
               annotation_text=".500 line")
fig1.update_layout(template="plotly_white", width=900, height=600)
fig1.write_html("interactive_scatter.html")
print("Chart 1 saved: interactive_scatter.html")

# CHART 2: Over/Under percentage by team — interactive bar chart
df_sorted = df.sort_values("Over_Pct", ascending=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=df_sorted["Team"], x=df_sorted["Over_Pct"],
    orientation="h",
    marker_color=["#d32f2f" if p < 45 else "#ff9800" if p < 55 else "#2e7d32" 
                   for p in df_sorted["Over_Pct"]],
    hovertemplate="%{y}<br>Over: %{x}%<br><extra></extra>"
))

fig2.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
fig2.update_layout(
    title="2017 NFL: Over/Under Hit Rate by Team",
    xaxis_title="Over %",
    template="plotly_white",
    width=900, height=700
)
fig2.write_html("interactive_overunder.html")
print("Chart 2 saved: interactive_overunder.html")

# CHART 3: Scoring trends across weeks
weekly_scores = []
for week in range(1, 18):
    week_games = season[season["schedule_week"] == str(week)]
    if len(week_games) == 0:
        week_games = season[season["schedule_week"] == week]
    if len(week_games) > 0:
        avg = round((week_games["score_home"].mean() + week_games["score_away"].mean()) / 2, 1)
        total_avg = round(week_games["score_home"].mean() + week_games["score_away"].mean(), 1)
        weekly_scores.append({"Week": week, "Avg_PPG": avg, "Avg_Total": total_avg})

wdf = pd.DataFrame(weekly_scores)

fig3 = px.line(wdf, x="Week", y="Avg_Total", markers=True,
               title="2017 NFL: Average Game Total by Week",
               labels={"Avg_Total": "Average Combined Score"})
fig3.add_hline(y=wdf["Avg_Total"].mean(), line_dash="dash", line_color="red",
               annotation_text=f"Season Avg: {round(wdf['Avg_Total'].mean(), 1)}")
fig3.update_layout(template="plotly_white", width=900, height=500)
fig3.write_html("interactive_weekly.html")
print("Chart 3 saved: interactive_weekly.html")

print("\nOpen any .html file in your browser to interact with the charts!")