import os
from os import listdir
from os.path import join, isfile
import sys
import numpy
import pandas
import datetime
import click

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

def getFileList(path, pattern=None, filetype=None, includePath=False):
    if not os.path.exists(path):
        print('Could not find path: {}'.format(path))
        sys.exit(1)
    includedPath = path if includePath else ''
    filenames = [join(path, name) for name in listdir(path) if isfile(join(path, name))]
    if filetype is not None:
        filenames = list(filter(lambda filename: filetype in filename, filenames))
    if pattern is not None:
        filenames = list(filter(lambda filename: pattern in filename.split('/')[-1], filenames))
    return filenames

def getDirectoryList(path, pattern=None):
    if not os.path.exists(path):
        raise Error('Could not find path: {}'.format(path))
    folders = [name for name in listdir(path) if not isfile(join(path, name))]
    if pattern is not None:
        folders = list(filter(lambda folder: pattern in folder, folders))
    return folders

def createInputAndOutput(currency, periods, interval):
    inputs = []
    years = []
    months = []
    for period in periods:
        year, month = period.split('_')
        if year not in years:
            years.append(year)
        if month not in months:
            months.append(month)
        inputs += getFileList(join('raw', currency, period), filetype='.csv', includePath=True)

    year = years[0] if len(years) == 1 else '{}-{}'.format(years[0], years[-1])
    month = months[0] if len(months) == 1 else '{}-{}'.format(months[0], months[-1])
    formattedInterval = '{}{}'.format(*interval.split(' '))
    output = join('data', '{}_{}_{}_{}.h5'.format(currency, year, month, formattedInterval))
    return inputs, output

@click.command()
@click.argument('periods')
@click.argument('interval')
@click.option('--pattern', help='Only sample currencies containing this pattern')
def main(periods, interval, pattern):
    currencies = getDirectoryList('raw', pattern=pattern)
    interval = '{} min'.format(interval)
    periods = periods.split(',')
    assert len(currencies) > 0 and len(periods) > 0 and interval is not None

    for currency in currencies:
        inputs, output = createInputAndOutput(currency, periods, interval)
        if os.path.isfile(output):
            answer = input(''.join(['The file "{}" already exists. Are you sure you want to ',
                           'overwrite (y/n)?']).format(output))
            if answer != 'y':
                print('Continuing with next file')
                continue
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
