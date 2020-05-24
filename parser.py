import pandas as pd
import numpy as np
import csv
import datetime
import matplotlib.pyplot as plt
from itertools import combinations
from scipy import stats
import sys
import csv

maxInt = sys.maxsize

while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)


def str_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


def dates_delta(date1, date2):
    return abs(date1 - date2)


def parse_file(filename):
    data = pd.read_csv(filename, encoding='latin-1')
    mydict = {}
    for device_name in data['device'].unique():
        mydict[device_name] = {}
        for _, row in data[data['device'] == device_name].iterrows():
            mydict[device_name][row['ts_date']] = int(row['gen_pd_anomaly'])
    return mydict


def dates_frequency(dict):
    dates_frequency_dict = {}
    for interface in dict.keys():
        for date in dict[interface].keys():
            if date not in dates_frequency_dict.keys():
                dates_frequency_dict[date] = 1
            else:
                dates_frequency_dict[date] += 1
    return dates_frequency_dict


def remove_dates(dict):
    maxDate = None
    for interface in dict.keys():
        minDate = min(dict[interface], key=dict[interface].get)
        if maxDate == None or minDate > maxDate:
            maxDate = minDate
    for interface in dict.keys():
        for date in list(dict[interface].keys()):
            if date < maxDate:
                del dict[interface][date]
    return dict


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


def frequency_to_range(dates_frequency_dict):
    range_dict = {}
    check_point_date = None
    check_point_freq = None
    last_date = None
    for date, freq in dates_frequency_dict.items():
        freq = int(freq)
        if check_point_date == None or check_point_freq == None:
            check_point_date = date
            check_point_freq = freq
        elif freq != check_point_freq:
            range_dict[check_point_date + ' to ' + last_date] = check_point_freq
            check_point_date = date
            check_point_freq = freq
        last_date = date
    range_dict[check_point_date + ' to ' + last_date] = check_point_freq
    return range_dict


def ranges_frequency_histogram(range_dict):
    write_dict(range_dict, 'dates_range_frequency')
    df = pd.DataFrame(range_dict.values(), index=range_dict.keys(), columns=['Frequency'])
    y = list(df['Frequency'])
    x = list(df.index)
    x_font = {'family': 'serif', 'color': 'black', 'weight': 'normal', 'size': 50, }
    y_font = {'family': 'serif', 'color': 'black', 'weight': 'normal', 'size': 30, }
    title_font = {'family': 'serif', 'color': 'black', 'weight': 'normal', 'size': 60, }
    y_name = 'Active Interfaces:'
    x_name = 'Dates Range'
    title = 'Active Interfaces Per Dates-Range:'
    fig = plt.figure(figsize=(80, 30))
    ax = fig.add_subplot(2, 1, 1)
    ax.set_xlabel(x_name, fontdict=x_font)
    ax.set_ylabel(y_name, fontdict=y_font)
    ax.set_title(title, fontdict=title_font)
    plt.plot(x, y)
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()


def remove_unrelevant_dates(mydict):
    start_date = datetime.datetime.strptime('2018-01-26', '%Y-%m-%d')
    end_date = datetime.datetime.strptime('2019-07-26', '%Y-%m-%d')

    for interface in list(mydict.keys()):
        if len(mydict[interface]) == 0:
            continue
        for date_anomaly in list(mydict[interface].keys()):
            date_only = datetime.datetime.strptime(date_anomaly.split(" ")[0], '%Y-%m-%d')
            if date_only < start_date or date_only > end_date:
                del mydict[interface][date_anomaly]
    for interface in list(mydict.keys()):
        if len(mydict[interface]) == 0:
            del mydict[interface]
    return mydict


def pearson_correlation(mydict):
    interfacePairs = list(combinations(mydict, 2))
    pearsonDict = {}
    counter = 0
    for interface1, interface2 in interfacePairs:
        counter += 1
        lstAnomallies1 = []
        lstAnomallies2 = []
        keyset1 = set(mydict[interface1].keys())
        keyset2 = set(mydict[interface2].keys())
        identicalDates = keyset1.intersection(keyset2)
        # should we have minimum identical dates?
        if len(identicalDates) > 1:
            for identicalDate in identicalDates:
                lstAnomallies1.append(mydict[interface1][identicalDate])
                lstAnomallies2.append(mydict[interface2][identicalDate])
            # lstAnomallies1 = np.array(lstAnomallies1)
            # lstAnomallies2 = np.array(lstAnomallies2)
            pearsonDict[(interface1, interface2)] = stats.pearsonr(lstAnomallies1, lstAnomallies2)[0]
        else:
            pearsonDict[(interface1, interface2)] = 0
    return pearsonDict


mydict = parse_file('netflow_data.csv')
# dates_frequency_dict = dates_frequency(mydict)
# write_dict(dates_frequency_dict, 'dates_frequency_dict')
# range_dict = frequency_to_range(read_dict('dates_frequency_dict'))
# ranges_frequency_histogram(range_dict)
# write_dict(mydict, 'before_remove')
# mydict_after_remove = remove_dates(mydict)
# write_dict(mydict_after_remove, 'after_remove')
relevant_anomalies = remove_unrelevant_dates(mydict)
write_dict(relevant_anomalies, 'relevant')

# Dictionary with pair of devices_interface and their Pearson Correlation score
# {{(Device_Interface , Device_Interface): score},....}
# relevant_anomalies = read_dict('relevant')
pearson_dict = pearson_correlation(relevant_anomalies)
write_dict(pearson_dict, 'pearson')
