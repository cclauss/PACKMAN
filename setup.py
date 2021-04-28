import packman
from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()

PACKAGES=['packman',
          'packman.molecule',
          'packman.anm',
          'packman.apps',
          'packman.bin',
          'packman.constants',
          'packman.utilities',
          'packman.entropy',
          'packman.tests',
          'packman.tests.anm',
          'packman.tests.data',
          'packman.tests.entropy',
          'packman.tests.molecule'
          ]

PACKAGE_DATA = {'packman.bin': ['logo.ico'],
                'packman.tests' : ['data/*.hng','data/*.pdb','data/*.cif']
}

SCRIPTS=['packman=packman.bin.PACKMAN:main']


setup(name='py-packman',
      version=packman.__version__,
      description='A software package for molecular PACKing and Motion ANalysis (PACKMAN)',
      url='https://github.com/Pranavkhade/PACKMAN',
      author='Pranav Khade',
      author_email='pranavk@iastate.edu',
      license='MIT',
      packages=PACKAGES,
      package_data=PACKAGE_DATA,
      long_description = long_description,
      long_description_content_type='text/markdown',
      keywords=('protein, dynamics, protein packing, protein domain, protein hinge'),
      classifiers=[
              'Intended Audience :: Education',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: MIT License',
              'Operating System :: MacOS',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2',
              'Programming Language :: Python :: 3',
              'Topic :: Scientific/Engineering :: Bio-Informatics',
              'Topic :: Scientific/Engineering :: Chemistry',
              'Topic :: Scientific/Engineering :: Mathematics'
                ],
      entry_points = {
              'console_scripts': SCRIPTS,
                },
    install_requires=['numpy', 'scipy', 'networkx', 'mlxtend', 'scikit-learn'],
      )