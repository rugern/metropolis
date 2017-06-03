import os
from os.path import join
from urllib.request import urlretrieve
from urllib.error import HTTPError
from zipfile import ZipFile
import click

monthMapping = {
    '1': '01%20January',
    '2': '02%20February',
    '3': '03%20March',
    '4': '04%20April',
    '5': '05%20May',
    '6': '06%20June',
    '7': '07%20July',
    '8': '08%20August',
    '9': '09%20September',
    '10': '10%20October',
    '11': '11%20November',
    '12': '12%20December',
}

allCurrencies = [
    'EUR_AUD',
    'EUR_CAD',
    'EUR_CHF',
    'EUR_CZK',
    'EUR_DKK',
    'EUR_GBP',
    'EUR_HUF',
    'EUR_JPY',
    'EUR_NOK',
    'EUR_NZD',
    'EUR_PLN',
    'EUR_SEK',
    'EUR_TRY',
    'EUR_USD',
]

weeks = [
    'Week1',
    'Week2',
    'Week3',
    'Week4',
    'Week5',
]

def assertOrCreateDirectory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def save(url, directory):
    print('Downloading {}'.format(url))
    try:
        response, headers = urlretrieve(url)
    except HTTPError:
        print('Not found, skipping this one: {}'.format(url))
        return

    print('Saving {} to {}'.format(url.split('/')[-1].split('.')[0], directory))
    zipped = ZipFile(response)
    for name in zipped.namelist():
        data = zipped.read(name)
        output = open(join(directory, name), 'wb')
        output.write(data)
        output.close()

@click.command()
@click.argument('year')
@click.argument('months')
@click.option('--pattern', help='Only download currencies containing this pattern')
def main(year, months, pattern):
    base = 'http://ratedata.gaincapital.com'
    months = list(map(lambda month: monthMapping[month], months.split(',')))
    currencies = list(filter(lambda currency: pattern in currency, allCurrencies))

    for month in months:
        for currency in currencies:
            for week in weeks:
                url = join(base, year, month, '{}_{}.zip'.format(currency, week))
                directory = join('raw', currency, '{}_{}'.format(year, month.split('%')[0]))
                assertOrCreateDirectory(directory)
                save(url, directory)

if __name__ == '__main__':
    main()
