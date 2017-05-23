import shutil
from os import listdir
from os.path import isfile, join
import sys

if __name__ == '__main__':
    answer = input('Are you sure you want to remove all folders in "data/" (y/n)?')
    if answer != 'y':
        sys.exit(0)

    path = 'data'
    for name in listdir(path):
        if not isfile(join(path, name)):
            shutil.rmtree(join(path, name))
    print('Finished successfully')
