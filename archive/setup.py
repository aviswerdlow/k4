#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="k4cli",
    version="1.0.0",
    description="K4 Kryptos validation and analysis CLI",
    author="K4 Research Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0", 
        "numpy>=1.24.0"
    ],
    entry_points={
        "console_scripts": [
            "k4=k4cli.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)