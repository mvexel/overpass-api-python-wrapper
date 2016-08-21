from codecs import open as codecs_open
from setuptools import setup, find_packages

# Get the long description from the relevant file
with codecs_open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='overpass',
    packages=['overpass'],
    version='0.5.0',
    description='Python wrapper for the OpenStreetMap Overpass API',
    long_description=long_description,
    author='Martijn van Exel',
    author_email='m@rtijn.org',
    url='https://github.com/mvexel/overpass-api-python-wrapper',
    license='Apache',
    keywords=['openstreetmap', 'overpass', 'wrapper'],
    classifiers=[
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Scientific/Engineering :: GIS',
    'Topic :: Utilities',
    ],
    install_requires=['requests>=2.3.0', 'geojson>=1.0.9'],
    extras_require={
        'test': ['pytest'],
    }
)
