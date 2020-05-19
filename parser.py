import pandas as pd
import csv
import datetime
import matplotlib.pyplot as plt

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
        if maxDate ==  None or minDate > maxDate:
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

# mydict = parse_file('netflow_data.csv')
# dates_frequency_dict = dates_frequency(mydict)
# write_dict(dates_frequency_dict, 'dates_frequency_dict')
# range_dict = frequency_to_range(read_dict('dates_frequency_dict'))
# ranges_frequency_histogram(range_dict)
# write_dict(dict, 'before_remove')
# dict = remove_dates(dict)
# write_dict(dict, 'after_remove')

