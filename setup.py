from setuptools import setup

setup(
    name="overpass",
    packages=["overpass"],
    version="0.7",
    description="Python wrapper for the OpenStreetMap Overpass API",
    long_description="See README.md",
    author="Martijn van Exel",
    author_email="m@rtijn.org",
    url="https://github.com/mvexel/overpass-api-python-wrapper",
    license="Apache",
    keywords=["openstreetmap", "overpass", "wrapper"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
    ],
    install_requires=["requests>=2.3.0", "osm2geojson"],
    extras_require={"test": ["pytest", "requests-mock[fixture]", "geojson>=1.0.9"]},
)
