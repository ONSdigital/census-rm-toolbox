from pathlib import Path

import setuptools

setuptools.setup(
    name="toolbox",
    version="5.1.0",
    description="Tools for the RM cluster",
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/census-rm-toolbox",
    packages=setuptools.find_packages(),
    install_requires=['termcolor']
)
