mahomes_yards = 4839
mahomes_tds = 37
mahomes_attempts = 564

stafford_yards = 4707
stafford_tds = 46
stafford_attempts = 597

mahomes_ypa = mahomes_yards / mahomes_attempts
stafford_ypa = stafford_yards / stafford_attempts

print("--- Yards Per Attempt ---")
print("Mahomes:", round(mahomes_ypa, 2))
print("Stafford:", round(stafford_ypa, 2))

# COMPARISON — who's better?
if mahomes_ypa > stafford_ypa:
    print("Mahomes has the higher YPA")
else:
    print("Stafford has the higher YPA")

# TD percentage
mahomes_td_pct = (mahomes_tds / mahomes_attempts) * 100
stafford_td_pct = (stafford_tds / stafford_attempts) * 100

print("\n--- TD Percentage ---")
print("Mahomes:", round(mahomes_td_pct, 2), "%")
print("Stafford:", round(stafford_td_pct, 2), "%")