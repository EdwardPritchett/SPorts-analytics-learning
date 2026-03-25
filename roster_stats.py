# Lists — store multiple values in one variable
players = ["Mahomes", "Stafford", "Allen", "Burrow", "Lamar", "Goff", "Prescott"]
yards = [4839, 4707, 4306, 4018, 3928, 4564, 4552]
tds = [37, 46, 40, 30, 41, 34,30]
attempts = [564, 597, 577, 516, 482, 578, 600]

# Loop — do something for EACH player
print("=== QB Report Card ===\n")

for i in range(len(players)):
    ypa = round(yards[i] / attempts[i], 2)
    td_pct = round((tds[i] / attempts[i]) * 100, 2)
    
    print(players[i])
    print("  Yards:", yards[i])
    print("  YPA:", ypa)
    print("  TD%:", td_pct, "%")
    
    if ypa > 8:
        print("  Verdict: Elite efficiency")
    elif ypa > 7:
        print("  Verdict: Above average")
    else:
        print("  Verdict: Needs improvement")
    
    print()  # blank line between players
    