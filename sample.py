import csv
with open("ratings_log.csv", mode="r", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = ["timestamp", "user_id", "rating", "summary", "sentiment"]
print(rows)