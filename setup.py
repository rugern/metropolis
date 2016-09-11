"""Run to install required packages and create module."""

from setuptools import setup

requirements = [
    'pyramid',
    'numpy',
    'matplotlib',
    'TA-Lib',
    'pandas',
    'tables',
    'flake8',
    'flake8-docstrings',
    'hacker',
    'Jinja2',
]

setup(name='metropolis',
      install_requires=requirements,
      entry_points="""\
      [paste.app_factory]
      main = metropolis:main
      """,
      )
