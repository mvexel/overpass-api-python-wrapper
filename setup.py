from setuptools import setup

setup(
    name="overpass",
    packages=["overpass"],
    version="0.7",
    description="Python wrapper for the OpenStreetMap Overpass API",
    long_description="See README.md",
    author="Alexandre Domingues (original author: Martijn van Exel)",
    author_email="adomingues@gmail.com",
    url="https://github.com/Taxuspt/overpass-api-python-wrapper",
    license="Apache",
    keywords=["openstreetmap", "overpass", "wrapper"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
    ],
    install_requires=["requests>=2.3.0", "geojson>=1.0.9", "shapely>=1.6.4", "osm2geojson>=0.1.17"],
    extras_require={"test": ["pytest"]},
)
