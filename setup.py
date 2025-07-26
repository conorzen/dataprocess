from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dataprocessing",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A user-friendly Python package for working with CSV data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dataprocessing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "chardet>=4.0.0",
        "python-dateutil>=2.8.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
        "pyarrow>=7.0.0",
        "requests>=2.25.0",
        "psycopg2-binary>=2.9.0",
        "mysql-connector-python>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "fast": [
            "polars>=0.19.0",
        ],
    },
    keywords="csv, data, pandas, user-friendly, data-analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dataprocessing/issues",
        "Source": "https://github.com/yourusername/dataprocessing",
        "Documentation": "https://github.com/yourusername/dataprocessing#readme",
    },
) 