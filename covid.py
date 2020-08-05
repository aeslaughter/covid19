#!/usr/bin/env python3
import argparse
import pandas
import math
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

def get_options():
    parser = argparse.ArgumentParser(description='Python tool for plotting US and US state COVID-19 data')
    parser.add_argument('--average', type=int, default=7,
                        help="Number of days to use for running average (default: 7)")
    parser.add_argument('--state', '-s', type=str,
                        help="The state data to display (e.g., ID for Idaho); if not provided the US data is shown.")
    parser.add_argument('--positive-start', type=int, default=1000,
                        help="Number of positive cases considered for starting the plots")
    return parser.parse_args()

def create_graphs(opt):
    if opt.state:
        prefix = opt.state.upper()
        url = 'https://covidtracking.com/api/v1/states/{}/daily.csv'.format(opt.state.lower())
        outfile = 'covid_{}.pdf'.format(opt.state)
    else:
        prefix = 'US'
        url = 'https://covidtracking.com/api/v1/us/daily.csv'
        outfile = 'covid_us.pdf'

    # Read the data from the URL
    df = pandas.read_csv(url)

    # Compute the indices to plot
    index = df['positive'] > opt.positive_start
    df = df[index]

    # Add the running averages and rate calculations
    df['infection_rate'] = df['positive'] / (df['positive'] + df['negative']) * 100
    df['infection_rate_avg'] = df['infection_rate'].rolling(window=opt.average, center=False).mean().shift(-opt.average)

    df['new_cases_avg'] = df['positiveIncrease'].rolling(window=opt.average, center=False).mean().shift(-opt.average)
    df['new_deaths_avg'] = df['deathIncrease'].rolling(window=opt.average, center=False).mean().shift(-opt.average)

    df['death_rate'] = df['death'] / df['positive'] * 100
    df['death_rate_avg'] = df['death_rate'].rolling(window=opt.average, center=False).mean().shift(-opt.average)

    # Extract the x-axis dates and create the figure
    date = pandas.to_datetime(df['date'], format='%Y%m%d').to_list()
    fig, axes = plt.subplots(2,2, figsize=(19.20, 10.80), dpi=100, tight_layout=True)

    # NEW CASES
    axes[0,0].plot_date(date, df['new_cases_avg'], 'k-', label='New Cases ({}-day avg.)'.format(opt.average))
    axes[0,0].bar(date, df['positiveIncrease'], label='New Cases')
    axes[0,0].set_title('{} COVID-19 New Positive Cases\n{}'.format(prefix, url))
    axes[0,0].set_ylabel('New Positive Cases')
    axes[0,0].legend()

    # NEW DEATHS
    axes[0,1].plot_date(date, df['new_deaths_avg'], 'k-', label='New Deaths ({}-day avg.)'.format(opt.average))
    axes[0,1].bar(date, df['deathIncrease'], label='New Deaths')
    axes[0,1].set_title('{} COVID-19 New Deaths\n{}'.format(prefix, url))
    axes[0,1].set_ylabel('New Deaths')
    axes[0,1].legend()

    # POSITIVE TEST RATE
    axes[1,0].plot_date(date, df['infection_rate_avg'], 'k-', label='Infection Rate ({}-day avg.)'.format(opt.average))
    axes[1,0].bar(date, df['infection_rate'], label='Infection Rate')
    axes[1,0].set_title('{} COVID-19 Positive Test Rate\n{}'.format(prefix, url))
    axes[1,0].set_ylabel('Infection Rate in % (Positive Tests : Total Tests)')
    axes[1,0].legend()

    # DEATH RATE
    axes[1,1].plot_date(date, df['death_rate_avg'], 'k-', label='Death Rate ({}-day avg.)'.format(opt.average))
    axes[1,1].bar(date, df['death_rate'], label='death Rate')
    axes[1,1].set_title('{} COVID-19 Death Rate\n{}'.format(prefix, url))
    axes[1,1].set_ylabel('Death Rate in % (Deaths : Positive Tests)')
    axes[1,1].legend()

    # Setup time axes and gird marks
    wks = math.ceil(len(date)/7) + 1
    start = date[-1] - datetime.timedelta(days=date[-1].weekday())
    xticks = [start + datetime.timedelta(days=i*7) for i in range(wks)]
    xtick_labels = [t.strftime('%Y-%m-%d') for t in xticks]

    for row in axes:
        for ax in row:
            ax.set_xticks(xticks)
            ax.set_xticks([start + datetime.timedelta(days=i) for i in range(7*wks)], minor=True)
            ax.set_xticklabels(xtick_labels, rotation='vertical')
            ax.grid(which='both', axis='both')
            ax.grid(which='minor', axis='both', linewidth=1, color=[0.9]*3)
            ax.grid(which='minor', axis='both', linewidth=1, color=[0.95]*3)

    fig.savefig(outfile)

if __name__ == '__main__':
    opt = get_options()
    create_graphs(opt)
