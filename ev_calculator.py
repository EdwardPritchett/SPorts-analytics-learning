def american_to_implied_prob(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100) * 100
    else:
        return 100 / (odds + 100) * 100

def calc_ev(your_prob, odds, bet_amount):
    if odds < 0:
        payout = bet_amount * (100 / abs(odds))
    else:
        payout = bet_amount * (odds / 100)
    
    ev = (your_prob / 100 * payout) - ((100 - your_prob) / 100 * bet_amount)
    return round(ev, 2)

# Get input from the user
print("=== Sports Betting EV Calculator ===\n")

odds = int(input("Enter the American odds (e.g. -110 or +150): "))
your_prob = float(input("Enter YOUR estimated win probability (e.g. 55): "))
bet_amount = float(input("Enter bet amount in dollars: "))

# Calculate
implied = round(american_to_implied_prob(odds), 2)
ev = calc_ev(your_prob, odds, bet_amount)

# Display results
print("\n--- Results ---")
print("Book's implied probability:", implied, "%")
print("Your estimated probability:", your_prob, "%")
print("Expected value: $" + str(ev))

if ev > 0:
    print("VERDICT: +EV bet! You have an edge.")
elif ev == 0:
    print("VERDICT: Break even.")
else:
    print("VERDICT: -EV bet. Pass on this one.")
    