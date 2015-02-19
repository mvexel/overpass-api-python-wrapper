from setuptools import setup

setup(
    name='overpass',
    packages=['overpass'],
    version='0.2.2',
    description='Python wrapper for the OpenStreetMap Overpass API',
    author='Martijn van Exel',
    author_email='m@rtijn.org',
    url='https://github.com/mvexel/overpass-api-python-wrapper',
    license='Apache',
    keywords=['openstreetmap', 'overpass', 'wrapper'],
    classifiers=[],
    install_requires=['click', 'requests>=2.3.0', 'geojson>=1.0.9'],
    extras_require={
        'test': ['pytest'],
    },
    entry_points="""
        [console_scripts]
        overpass=overpass.cli:cli
"""
)
