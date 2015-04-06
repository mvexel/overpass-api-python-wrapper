from setuptools import setup

setup(
    name='overpass',
    packages=['overpass'],
    version='0.2.3',
    description='Python wrapper for the OpenStreetMap Overpass API',
    author='Martijn van Exel',
    author_email='m@rtijn.org',
    mantainer='Wille Marcel',
    mantainer_email='wille@wille.blog.br',
    url='https://github.com/willemarcel/overpass-api-python-wrapper',
    license='Apache',
    keywords=['openstreetmap', 'overpass', 'wrapper'],
    classifiers=[
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Scientific/Engineering :: GIS',
    'Topic :: Utilities',
    ],
    install_requires=['click', 'requests>=2.3.0', 'geojson>=1.0.9'],
    extras_require={
        'test': ['pytest'],
    },
    entry_points="""
        [console_scripts]
        overpass=overpass.cli:cli
"""
)
