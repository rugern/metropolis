import click

from optimize.test import testRunner

@click.group()
def main():
    pass

@main.command()
@click.option('--pattern', default='2017_05_5min', help='Pattern of data files to test on')
@click.option('--money', type=int, default=10000, help='Amount of EUR to start with')
@click.option('--search', is_flag=True, help='Perform gridsearch')
def test(pattern, money, search):
    testRunner(pattern, money, search)

if __name__ == '__main__':
    main()
