import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

url = "https://raw.githubusercontent.com/slieb74/NFL-Betting-Data/master/nfl_betting_df.csv"
games = pd.read_csv(url)

# ============================================
# STEP 1: PREPARE THE DATA
# ============================================
print("=== Step 1: Preparing Data ===\n")

# Use seasons 2000-2017 for more data, filter out missing values
df = games[(games["schedule_season"] >= 2000) & (games["schedule_season"] <= 2017)].copy()
df = df.dropna(subset=["home_win_pct", "away_win_pct", "spread_favorite", 
                         "over_under_line", "h_ppg", "a_ppg", "h_papg", "a_papg"])

# Create the TARGET — what we're trying to predict
# 1 = home team wins, 0 = home team loses
df["home_win"] = (df["score_home"] > df["score_away"]).astype(int)

print(f"Total games: {len(df)}")
print(f"Home wins: {df['home_win'].sum()} ({round(df['home_win'].mean()*100, 1)}%)")
print(f"Away wins: {len(df) - df['home_win'].sum()} ({round((1-df['home_win'].mean())*100, 1)}%)")

# ============================================
# STEP 2: FEATURE ENGINEERING
# ============================================
print("\n=== Step 2: Selecting Features ===\n")

# These are the stats we think predict who wins
features = ["home_win_pct", "away_win_pct", "h_ppg", "a_ppg", 
            "h_papg", "a_papg", "home_pt_diff_pg", "away_pt_diff_pg",
            "home_win_pct_last_4", "away_win_pct_last_4"]

X = df[features]  # The input data (stats)
y = df["home_win"]  # The target (did home team win?)

print(f"Features we're using: {len(features)}")
for f in features:
    print(f"  - {f}")

# ============================================
# STEP 3: SPLIT INTO TRAINING AND TESTING
# ============================================
print("\n=== Step 3: Train/Test Split ===\n")

# 80% of games to TRAIN the model, 20% to TEST it
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training games: {len(X_train)}")
print(f"Testing games: {len(X_test)}")
print("(Model learns from training data, we evaluate on test data it's never seen)")

# ============================================
# STEP 4: TRAIN THE MODEL
# ============================================
print("\n=== Step 4: Training Logistic Regression ===\n")

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

print("Model trained!")

# See which features matter most
feature_importance = pd.DataFrame({
    "Feature": features,
    "Weight": model.coef_[0]
}).sort_values("Weight", key=abs, ascending=False)

print("\nFeature Importance (what the model learned):")
for _, row in feature_importance.iterrows():
    direction = "+" if row["Weight"] > 0 else ""
    print(f"  {row['Feature']}: {direction}{round(row['Weight'], 3)}")

# ============================================
# STEP 5: TEST THE MODEL
# ============================================
print("\n=== Step 5: Model Performance ===\n")

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {round(accuracy * 100, 1)}%")
print(f"(Baseline: always pick home team = {round(df['home_win'].mean()*100, 1)}%)")
print(f"Model beats baseline by: {round((accuracy - df['home_win'].mean()) * 100, 1)} percentage points")

print("\nDetailed Report:")
print(classification_report(y_test, y_pred, target_names=["Away Win", "Home Win"]))

# ============================================
# STEP 6: MAKE PREDICTIONS
# ============================================
print("=== Step 6: Predict a Game ===\n")

# Simulate: Strong home team vs weak away team
matchup = pd.DataFrame({
    "home_win_pct": [0.750],      # home team wins 75%
    "away_win_pct": [0.375],      # away team wins 37.5%
    "h_ppg": [27.5],              # home scores 27.5 ppg
    "a_ppg": [19.2],              # away scores 19.2 ppg
    "h_papg": [20.1],             # home allows 20.1 ppg
    "a_papg": [25.8],             # away allows 25.8 ppg
    "home_pt_diff_pg": [7.4],     # home team +7.4 per game
    "away_pt_diff_pg": [-6.6],    # away team -6.6 per game
    "home_win_pct_last_4": [1.0], # home team won last 4
    "away_win_pct_last_4": [0.25] # away team won 1 of last 4
})

prediction = model.predict(matchup)[0]
probability = model.predict_proba(matchup)[0]

print("Matchup: Strong Home Team vs Weak Road Team")
print(f"Prediction: {'HOME WIN' if prediction == 1 else 'AWAY WIN'}")
print(f"Confidence: Home {round(probability[1]*100, 1)}% — Away {round(probability[0]*100, 1)}%")

# ============================================
# STEP 7: RANDOM FOREST — MORE POWERFUL MODEL
# ============================================
from sklearn.ensemble import RandomForestClassifier

print("\n=== Step 7: Random Forest Model ===\n")

rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)
rf_accuracy = accuracy_score(y_test, rf_pred)

print(f"Logistic Regression Accuracy: {round(accuracy * 100, 1)}%")
print(f"Random Forest Accuracy:       {round(rf_accuracy * 100, 1)}%")
print(f"Improvement:                  {round((rf_accuracy - accuracy) * 100, 1)} points")

# Random Forest tells you feature importance differently
rf_importance = pd.DataFrame({
    "Feature": features,
    "Importance": rf_model.feature_importances_
}).sort_values("Importance", ascending=False)

print("\nRandom Forest Feature Importance:")
for _, row in rf_importance.iterrows():
    bar = "#" * int(row["Importance"] * 100)
    print(f"  {row['Feature']:25s} {round(row['Importance']*100, 1)}%  {bar}")

# Compare predictions on the same matchup
rf_prob = rf_model.predict_proba(matchup)[0]
print(f"\n--- Same Matchup Comparison ---")
print(f"Logistic Regression: Home {round(probability[1]*100, 1)}% — Away {round(probability[0]*100, 1)}%")
print(f"Random Forest:       Home {round(rf_prob[1]*100, 1)}% — Away {round(rf_prob[0]*100, 1)}%")

# ============================================
# STEP 8: BACKTESTING — WOULD THIS MAKE MONEY?
# ============================================
print("\n=== Step 8: Backtesting as a Betting Strategy ===\n")

# Get model's predicted probabilities for every test game
probabilities = model.predict_proba(X_test)

# Simulate betting: only bet when model is confident (>60% one way)
bankroll = 1000
bet_size = 20
wins = 0
losses = 0
bets_placed = 0

test_df = df.loc[X_test.index].copy()
test_df["model_home_prob"] = probabilities[:, 1]

for idx, row in test_df.iterrows():
    home_prob = row["model_home_prob"]
    
    # Only bet when model is confident
    if home_prob > 0.60:
        # Bet on home team
        bets_placed += 1
        if row["score_home"] > row["score_away"]:
            bankroll += bet_size * 0.91  # standard -110 odds payout
            wins += 1
        else:
            bankroll -= bet_size
            losses += 1
    elif home_prob < 0.40:
        # Bet on away team
        bets_placed += 1
        if row["score_away"] > row["score_home"]:
            bankroll += bet_size * 0.91
            wins += 1
        else:
            bankroll -= bet_size
            losses += 1

win_pct = round(wins / bets_placed * 100, 1) if bets_placed > 0 else 0
profit = round(bankroll - 1000, 2)

print(f"Starting bankroll: $1,000")
print(f"Bet size: ${bet_size} per game")
print(f"Confidence threshold: 60%")
print(f"\nResults:")
print(f"  Bets placed: {bets_placed} out of {len(X_test)} games")
print(f"  Record: {wins}-{losses}")
print(f"  Win rate: {win_pct}%")
print(f"  Final bankroll: ${round(bankroll, 2)}")
print(f"  Profit/Loss: {'$' + str(profit) if profit >= 0 else '-$' + str(abs(profit))}")
print(f"  ROI: {round(profit / (bets_placed * bet_size) * 100, 1)}%")

if profit > 0:
    print("\n  MODEL IS PROFITABLE!")
else:
    print(f"\n  Model lost money. Need better features or higher confidence threshold.")
    print("  Try changing the threshold to 0.65 and see what happens.")
