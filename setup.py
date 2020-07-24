from pathlib import Path

import setuptools

setuptools.setup(
    name="toolbox",
    version="4.1.0a",
    description="A treasure trove of python goodies",
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/census-rm-toolbox",
    packages=setuptools.find_packages(),
)
