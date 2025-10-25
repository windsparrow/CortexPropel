from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cortex-propel",
    version="0.1.0",
    author="CortexPropel Team",
    author_email="team@cortexpropel.com",
    description="An intelligent task management agent powered by LangGraph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cortexpropel/cortex-propel",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cortex-propel=cortex_propel.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cortex_propel": ["templates/*.json", "config/*.json"],
    },
)