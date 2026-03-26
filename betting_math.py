import pandas as pd
import math

# ============================================
# 1. BASIC STATISTICS
# ============================================
print("=== Basic Statistics ===\n")

# Points scored by a team across a season
scores = [27, 17, 31, 24, 20, 35, 14, 28, 21, 33, 24, 17, 30, 27, 19, 23, 28]

mean = sum(scores) / len(scores)
scores_sorted = sorted(scores)
median = scores_sorted[len(scores) // 2]

# Standard deviation — measures how spread out the scores are
variance = sum((x - mean) ** 2 for x in scores) / len(scores)
std_dev = math.sqrt(variance)

print(f"Scores: {scores}")
print(f"Mean (average): {round(mean, 1)}")
print(f"Median (middle value): {median}")
print(f"Std Deviation: {round(std_dev, 1)}")
print(f"\nWhat this means:")
print(f"  This team averages {round(mean, 1)} points per game")
print(f"  But their scores typically vary by +/- {round(std_dev, 1)} points")
print(f"  So on any given game, expect roughly {round(mean - std_dev, 1)} to {round(mean + std_dev, 1)} points")

# ============================================
# 2. PROBABILITY FUNDAMENTALS
# ============================================
print("\n\n=== Probability for Betting ===\n")

# If a team wins 60% at home and the opponent wins 45% on the road
home_win_rate = 0.60
away_win_rate = 0.45
away_loss_rate = 1 - away_win_rate  # 55% — how often the away team loses

# Simple probability estimate
combined_prob = (home_win_rate + away_loss_rate) / 2
print(f"Home team wins {home_win_rate*100}% at home")
print(f"Away team loses {away_loss_rate*100}% on the road")
print(f"Simple combined estimate: {round(combined_prob*100, 1)}% home team wins")

# ============================================
# 3. KELLY CRITERION
# ============================================
print("\n\n=== Kelly Criterion (Optimal Bet Sizing) ===\n")

def kelly_criterion(your_prob, american_odds):
    """Calculate optimal bet size as % of bankroll"""
    # Convert American odds to decimal
    if american_odds > 0:
        decimal_odds = (american_odds / 100) + 1
    else:
        decimal_odds = (100 / abs(american_odds)) + 1
    
    # Kelly formula: f = (bp - q) / b
    # b = decimal odds - 1 (net profit per dollar)
    # p = your probability of winning
    # q = probability of losing (1 - p)
    b = decimal_odds - 1
    p = your_prob / 100
    q = 1 - p
    
    kelly = (b * p - q) / b
    
    return {
        "decimal_odds": round(decimal_odds, 3),
        "kelly_pct": round(max(kelly, 0) * 100, 2),
        "half_kelly": round(max(kelly, 0) * 100 / 2, 2),
        "edge": round((p * decimal_odds - 1) * 100, 2)
    }

# Example bets
bets = [
    {"name": "Chiefs -3 vs Raiders", "prob": 58, "odds": -110},
    {"name": "Lions ML vs Bears", "prob": 65, "odds": -150},
    {"name": "Underdog Jags +7", "prob": 45, "odds": +110},
    {"name": "Trap game — no edge", "prob": 50, "odds": -110},
]

for bet in bets:
    result = kelly_criterion(bet["prob"], bet["odds"])
    print(f"{bet['name']}")
    print(f"  Your prob: {bet['prob']}% | Odds: {bet['odds']} | Decimal: {result['decimal_odds']}")
    print(f"  Edge: {result['edge']}% | Full Kelly: {result['kelly_pct']}% | Half Kelly: {result['half_kelly']}%")
    if result['kelly_pct'] == 0:
        print(f"  VERDICT: No edge. Don't bet.")
    elif result['half_kelly'] < 2:
        print(f"  VERDICT: Small edge. Bet light.")
    else:
        print(f"  VERDICT: Good edge. Bet {result['half_kelly']}% of bankroll.")
    print()

# ============================================
# 4. POISSON DISTRIBUTION
# ============================================
print("\n=== Poisson Distribution (Score Modeling) ===\n")

def poisson_prob(expected, actual):
    """Probability of scoring exactly 'actual' points given 'expected' average"""
    return (expected ** actual) * math.exp(-expected) / math.factorial(actual)

# If a team averages 24 PPG, what's the probability of each score?
avg_ppg = 24

print(f"Team averages {avg_ppg} PPG. Score probabilities:")
print()
for pts in range(14, 36):
    prob = poisson_prob(avg_ppg, pts) * 100
    bar = "#" * int(prob * 2)
    print(f"  {pts} pts: {round(prob, 1)}%  {bar}")

# Use Poisson for over/under
print(f"\n--- Over/Under Prediction ---")
team_a_avg = 27.5  # offense
team_b_avg = 21.0  # offense
total_line = 46.5

expected_total = team_a_avg + team_b_avg
print(f"Team A averages {team_a_avg} PPG, Team B averages {team_b_avg} PPG")
print(f"Expected total: {expected_total}")
print(f"Line: {total_line}")

if expected_total > total_line:
    print(f"MODEL SAYS: OVER (expected {expected_total - total_line} points above the line)")
else:
    print(f"MODEL SAYS: UNDER (expected {total_line - expected_total} points below the line)")