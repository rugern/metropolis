from setuptools import setup


requires = [
    'pyramid',
]

setup(name='metropolis',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = metropolis:main
      """,
)
