from setuptools import setup

setup(
    name='overpass',
    packages=['overpass'],
    version='0.0.1',
    description='Python wrapper for the OpenStreetMap Overpass API',
    author='Martijn van Exel',
    author_email='m@rtijn.org',
    url='https://github.com/mvexel/overpass-api-python-wrapper',
    download_url='https://github.com/mvexel/overpass-api-python-wrapper/tarball/0.0.1',
    keywords=['openstreetmap', 'overpass', 'wrapper'],
    classifiers=[],
    install_requires=['requests>=2.3.0', 'shapely>=1.4.3'],
)
