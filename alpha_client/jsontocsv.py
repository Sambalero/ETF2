import json
import csv


def convert():
    filename = filename = "./json/processed/summary " + "" + " - " + "" + ".json"

    f = open(filename)
    export = json.load(f)
    f.close()

    with open('export.csv', "w") as csv_out:
        writer = csv.writer(csv_out)

        count = 0
        for date in export:
            if count == 0:
                header = ["date"]
                header.extend(export[date].keys())
                writer.writerow(header)
                count += 1
            row = [date]
            row.extend(export[date].values())
            writer.writerow(row)
# python -c 'from jsontocsv import convert; convert()'
