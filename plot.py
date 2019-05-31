from matplotlib.dates import DateFormatter
import datetime
import json
import matplotlib.pyplot as plt


def extract_bowling_data(json_file, org_file):
    '''Extract bowling data from org file into JSON.'''
    with open(org_file, 'r') as source:
        lines = source.readlines()
        date = ''
        data = []
        for line in lines:
            # Date information
            if line.startswith('*'):
                date = line.strip('*').strip()
            # Bowling information
            elif 'bowling' in line and date is not '':
                scores = []
                start = line.find("(") + 1
                end = line.find(")")
                if start != 0:
                    scores = line[start:end].split(',')
                    scores = list(map(int, scores))
                data.append({'date': date, 'scores': scores})
        with open(json_file, 'w') as output:
            json.dump(data, output)


def gen_plots(json_file, from_org=False, org_file=''):
    '''Generate plots of bowling data.'''
    if from_org:
        extract_bowling_date(json_file, org_file)

    fig, ax = plt.subplots()
    # Individual points
    multi_dates = []
    ind_scores = []
    # Summary points
    dates = []
    min_scores = []
    avg_scores = []
    max_scores = []

    with open(json_file, 'r') as data:
        data = json.load(data)
        for item in data:
            date, scores = item['date'], item['scores']
            if scores:
                date = datetime.datetime.strptime(date, '%b %d, %Y').date()

                multi_dates += [date] * len(scores)
                ind_scores += scores
                dates.append(date)
                min_scores.append(min(scores))
                avg_scores.append(sum(scores)/len(scores))
                max_scores.append(max(scores))

    plt.plot_date(multi_dates, ind_scores, color='black')
    plt.plot_date(dates, min_scores, color='red')
    plt.plot_date(dates, avg_scores, color='blue')
    plt.plot_date(dates, max_scores, color='green')

    formatter = DateFormatter('%m/%d/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    plt.show()
