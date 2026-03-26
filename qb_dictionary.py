# A dictionary bundles all of a player's info together
mahomes = {
    "name": "Patrick Mahomes",
    "team": "KC",
    "yards": 4839,
    "tds": 37,
    "attempts": 564
}

stafford = {
    "name": "Matthew Stafford",
    "team": "LAR",
    "yards": 4707,
    "tds": 46,
    "attempts": 597
}

allen = {
     "name": "Josh Allen" , 
     "team": "BUF",
     "yards": 3668,
     "tds": 40,
     "attempts": 460,
}

burrow = {
    "name": "Joe Burrow",
    "team": "CIN",
    "yards": 1809,
    "tds": 17,
    "attempts": 259,
}

jackson = {
        "name": "Lamar Jackson",
        "team": "BAL",
        "yards": 2549,
        "tds": 21,
        "attempts": 302,
}

goff = {
    "name": "Jared Goff",
    "team": "DET",
    "yards": 4564,
    "tds": 34,
    "attempts": 578,
}

prescott = {
    "name": "Dak Prescott",
    "team": "DAL",
    "yards": 4552,
    "tds": 30,
    "attempts": 600,
}

def analyze_qb(qb):
    ypa = round(qb["yards"] / qb["attempts"], 2)
    td_pct = round((qb["tds"] / qb["attempts"]) * 100, 2)
    
    if ypa > 8:
        tier = "Elite"
    elif ypa > 7:
        tier = "Above Average"
    else:
        tier = "Needs Improvement"
    
    return {
        "name": qb["name"],
        "team": qb["team"],
        "ypa": ypa,
        "td_pct": td_pct,
        "tier": tier
    }


# Access any stat using its key
print(mahomes["name"], "-", mahomes["team"])
print("Yards:", mahomes["yards"])

# You can do math with dictionary values
mahomes_ypa = round(mahomes["yards"] / mahomes["attempts"], 2)
print("YPA:", mahomes_ypa)

# Now put multiple players in a LIST of dictionaries
qbs = [mahomes, stafford, allen, burrow, jackson, goff, prescott]

# Loop through them
print("\n=== Full QB Report ===\n")
for qb in qbs:
    result = analyze_qb(qb)
    print(result["name"], "(" + result["team"] + ")")
    print("  YPA:", result["ypa"])
    print("  TD%:", result["td_pct"], "%")
    print("  Tier:", result["tier"])
    print()