import json
import csv

f = open('emacd3.json')
emacd3 = json.load(f)
f.close()


with open('emacd3.csv', "w") as csv_out:
    writer = csv.writer(csv_out)

    count = 0
    for date in emacd3:
        if count == 0:
            header = ["date"]
            header.extend(emacd3[date].keys())
            writer.writerow(header)
            count += 1
        row = [date]
        row.extend(emacd3[date].values())
        writer.writerow(row)
# emacd3.close()
