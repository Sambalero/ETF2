import json
import csv
from analysis import dates_from_keys

def convert(inputfile=None, inputobject=None, outputfile=None, linekey=None): 

    if inputobject:
        export = inputobject
    elif inputfile:
        f = open(inputfile)
        export = json.load(f)
        f.close()
    else:
        raise UnboundLocalError("No input to convert")

    # print("outputfile: ", outputfile)

    with open(outputfile, "w") as csv_out:
        writer = csv.writer(csv_out)
        count = 0
        for line in export:
            if count == 0:
                if linekey:
                    header = [linekey]
                else:
                    header = []
                header.extend(export[line].keys())
                writer.writerow(header)
                count += 1
            # import pdb; pdb.set_trace()
            row = [line]
            try:
                row.extend(export[line].values())
            except:
                if line == 'note':
                    pass
            writer.writerow(row)

def convertranked(inputfile=None, inputobject=None, outputfile=None, linekey=None): 

    if inputobject:
        export = inputobject
    elif inputfile:
        f = open(inputfile)
        export = json.load(f)
        f.close()
    else:
        raise UnboundLocalError("No input to convert")

    with open(outputfile, "w") as csv_out:
        writer = csv.writer(csv_out)
        count = 0
        # import pdb; pdb.set_trace()
        for line in export:
            # print("export[line]: ", export[line])
            if count == 0:
                if linekey:
                    header = ["date", linekey]
                else:
                    header = [] 
                header.extend(export[line][list(export[line].keys())[0]].keys())
                writer.writerow(header)
                count += 1
            # import pdb; pdb.set_trace()
            for obj in export[line]:
                row = [line, obj] 
                row.extend(export[line][obj].values())
                writer.writerow(row)

def convert_list(inputfile=None, inputobject=None, outputfile=None, linekey=None): 

    if inputobject:
        export = inputobject
    elif inputfile:
        f = open(inputfile)
        export = json.load(f)
        f.close()
    else:
        raise UnboundLocalError("No input to convert")

    with open(outputfile, "w") as csv_out:
        writer = csv.writer(csv_out)
        count = 0
        if linekey:
            header = [linekey]
        else:
            header = []
        header.extend(export[0].keys())
        writer.writerow(header)
        for line in export:
            row = [line.values()]
            writer.writerow(row)


def btconvert(inputfile=None, inputobject=None, outputfile=None, linekey=None): 

    if inputobject:
        import collections
        export = collections.OrderedDict(inputobject)
    elif inputfile:
        f = open(inputfile)
        export = json.load(f)
        f.close()
    else:
        raise UnboundLocalError("No input to convert")


    with open(outputfile, "w", newline='') as csv_out:
        writer = csv.writer(csv_out)
        count = 0
        dates = list(reversed(sorted(dates_from_keys(export.keys()))))
        # import pdb; pdb.set_trace()
        for date in dates[::-1]:  # this could be date in dates and reverse here if needed
            if count == 0:
                if linekey:
                    header = [linekey]
                else:
                    header = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                # header.extend(export[line].keys())
                writer.writerow(header)
                count += 1
            row = [date]
            row.extend(list(export[date].values())[0: 4])
            row.extend([export[date]['4. close'], export[date]['5. volume']])
            # print(date)
            writer.writerow(row)

def btconvert_with_rank(inputfile=None, inputobject=None, outputfile=None, linekey=None): 

    if inputobject:
        export = inputobject
    elif inputfile:
        f = open(inputfile)
        export = json.load(f)
        f.close()
    else:
        raise UnboundLocalError("No input to convert")

    with open(outputfile, "w", newline='') as csv_out:
        writer = csv.writer(csv_out)
        count = 0
        dates = list(sorted(dates_from_keys(export.keys()))) # ascending old to new  
        # import pdb; pdb.set_trace()
        for index, date in enumerate(dates): 
            if index == 0:
                if linekey:
                    header = [linekey]
                else:
                    header = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'rank2', 'rank20', 'rank130']
                writer.writerow(header)
            else:  # we skip the first date since it has no rank value.
                row = [date]
                row.extend(list(export[date].values())[0: 4])
                row.extend([export[date]['4. close'], export[date]['5. volume'], export[date]['rank2'], export[date]['rank20'], export[date]['rank130']])
                writer.writerow(row)

# python -c 'from jsontocsv import convert; convert()'

# can generalize with this:

# def dict_depth(d):
#     if isinstance(d, dict):
#         return 1 + (max(map(dict_depth, d.values())) if d else 0)
#     return 0
# dic = {'a':1, 'b': {'c': {'d': {}}}}
# print(dict_depth(dic))

# https://www.w3resource.com/python-exercises/list/python-data-type-list-exercise-70.php

def debugvert():
    convert(inputfile="./json/prices/" + "AIA" + ".json", inputobject=None, outputfile="./json/fundata/222.csv", linekey=None)

#python -c 'from jsontocsv import debugvert; debugvert()'

'''json.dump(fundata, open("./json/fundata/111.json", "w"))'''