from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "pandas>=1.5.0",
        "chardet>=4.0.0",
        "python-dateutil>=2.8.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
        "pyarrow>=7.0.0",
        "requests>=2.25.0",
        "psycopg2-binary>=2.9.0",
        "mysql-connector-python>=8.0.0",
    ]

setup(
    name="dataprocesslite",
    version="0.1.0",
    author="Conor Reidy",
    author_email="conor@example.com",
    description="A user-friendly Python package for working with CSV data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conorzen/dataprocess",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "fast": ["polars>=0.19.0"],
    },
    keywords="csv, data, processing, pandas, sql, live-data",
    project_urls={
        "Bug Reports": "https://github.com/conorzen/dataprocess/issues",
        "Source": "https://github.com/conorzen/dataprocess",
        "Documentation": "https://github.com/conorzen/dataprocess#readme",
    },
) 