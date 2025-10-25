
from setuptools import setup, find_packages

setup(
    name="cortexpropel",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "litellm",
        "pydantic",
    ],
    entry_points='''
        [console_scripts]
        cortex=cortexpropel.main:cli
    ''',
)
