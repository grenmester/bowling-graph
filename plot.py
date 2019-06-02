from matplotlib.dates import DateFormatter
import click
import datetime
import json
import matplotlib.pyplot as plt
import os
import statistics


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


@click.command()
@click.argument('json-file', type=click.Path())
@click.option('-o', '--org-file', default='', type=click.Path(),
              help='Path to org file with bowling data. If this option is '
              'provided, a JSON file with the name `JSON_FILE\' will be '
              'generated and used. If this option is not provided, data will '
              'be read from `JSON_FILE\'.')
def gen_plots(json_file, org_file):
    '''
    Given a JSON file containing bowling data, generate plots analyzing the
    data. The JSON file can be generated from an org file.
    '''
    if org_file:
        extract_bowling_data(json_file, org_file)

    # Individual points
    multi_dates = []
    ind_scores = []
    # Summary points
    dates = []
    min_scores = []
    avg_scores = []
    std_scores = []
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
                std_scores.append(statistics.pstdev(scores))
                max_scores.append(max(scores))

    os.makedirs('output', exist_ok=True)

    fig, ax = plt.subplots()
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('All Scores')
    formatter = DateFormatter('%m/%d/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30)
    plt.plot_date(multi_dates, ind_scores, color='black')
    plt.savefig('output/graph1.png')
    plt.show()

    fig, ax = plt.subplots()
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('Average Scores')
    formatter = DateFormatter('%m/%d/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30)
    plt.errorbar(dates, avg_scores, std_scores, capsize=3, capthick=1,
                 color='black', elinewidth=1, marker='o', markersize=3)
    plt.savefig('output/graph2.png')
    plt.show()

    fig, ax = plt.subplots()
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('Summary')
    formatter = DateFormatter('%m/%d/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30)
    plt.plot_date(dates, min_scores, fmt='r-', label='min')
    plt.plot_date(dates, avg_scores, fmt='b-', label='avg')
    plt.plot_date(dates, max_scores, fmt='g-', label='max')
    plt.legend()
    plt.savefig('output/graph3.png')
    plt.show()


if __name__ == '__main__':
    gen_plots()
