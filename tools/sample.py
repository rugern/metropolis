import os
from os import listdir
from os.path import join, isfile
import sys
import numpy
import pandas
import datetime
import click

sys.path.insert(1, os.path.join(sys.path[0], '../sample'))

from utility.diskIO import getFileList, getDirectoryList

def dateparse(timestamp):    
    return datetime.datetime.fromtimestamp(float(timestamp))

def sample(data, interval, pad=False):
    result = data.resample(interval).ohlc()
    if pad:
        return result.fillna(method='pad')
    return result

def readCsv(infile):
    # return pandas.read_csv(infile, usecols=[0, 1], header=None, names=['DateTime', 'Buy'], index_col=0, parse_dates=True, date_parser=dateparse)
    return pandas.read_csv(infile, usecols=[3, 4, 5], header=0, names=['DateTime', 'Bid', 'Ask'], index_col=0, parse_dates=True)

def createInputAndOutput(currency, periods, interval, pattern=None):
    inputs = []
    years = []
    months = []
    for period in periods:
        year, month = period.split('_')
        if year not in years:
            years.append(year)
        if month not in months:
            months.append(month)
        inputs += getFileList(join('raw', currency, period), filetype='.csv', includePath=True, pattern=pattern)

    year = years[0] if len(years) == 1 else '{}-{}'.format(years[0], years[-1])
    periods = '{}'.format(months[0] if len(months) == 1 else '{}-{}'.format(months[0], months[-1]))
    if pattern is not None:
        weeks = pattern.split('|')
        periods += '_{}'.format(weeks[0] if len(weeks) == 1 else '{}-{}'.format(weeks[0], weeks[-1]))
    formattedInterval = '{}{}'.format(*interval.split(' '))
    output = join('data', '{}_{}_{}_{}.h5'.format(currency, year, periods, formattedInterval))
    return inputs, output

@click.command()
@click.argument('periods')
@click.argument('interval')
@click.option('--weeks', help='Select only this subset of weeks in a month')
@click.option('--pattern', help='Only sample currencies containing this pattern')
def main(periods, interval, weeks, pattern):
    periods = periods.split(',')
    interval = '{} min'.format(interval)
    weekPattern = None
    if weeks is not None:
        weekPattern = '|'.join(weeks.split(','))
    currencies = getDirectoryList('raw', pattern=pattern)

    assert len(currencies) > 0 and len(periods) > 0 and interval is not None
    assert weekPattern is None or len(periods) == 1

    for currency in currencies:
        inputs, output = createInputAndOutput(currency, periods, interval, pattern=weekPattern)
        print('Reading CSV for {}'.format(currency))
        raws = map(readCsv, inputs)
        raw = pandas.concat(raws)

        # print('Filtering by date')
        # filtered = raw.ix['2016-07-01':'2016-07-31']

        print('Sampling {}'.format(currency))
        pad = True
        sampled = sample(raw, interval, pad)

        print('Writing {} to HDF5'.format(currency))
        sampled.to_hdf(output, key='currency')

if __name__ == '__main__':
    main()
    print('Complete!')
