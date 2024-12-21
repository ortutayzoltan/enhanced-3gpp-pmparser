#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="enhanced-3gpp-pmparser",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Enhanced 3GPP Performance Measurement XML Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/enhanced-3gpp-pmparser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Telecommunications",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pmparser=pmparser.cli:main",
        ],
    },
)