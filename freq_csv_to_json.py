import csv
import json

with open("jp_freq.csv", newline="") as csvfile:
    freq = {}
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        freq[row[2]] = int(row[1])

with open("jp_freq.json", "w", encoding="utf-8") as file:
    json.dump({"words": freq}, file, indent=4, ensure_ascii=False)
