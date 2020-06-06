import csv
import sys

maxInt = sys.maxsize

while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

def write_dict(dict, filename):
    with open(filename + '.csv', 'w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict.items():
            writer.writerow([key, value])


def read_dict(filename):
    with open(filename + '.csv') as csv_file:
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        return mydict