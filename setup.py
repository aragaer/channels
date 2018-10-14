#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="yet-another-io-channels-library",
    version="0.1.0",
    author="Ilya Konovalov",
    author_email="aragaer@gmail.com",
    description="Simple IO channels library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="socket pipe",
    url="https://github.com/aragaer/channels",
    packages=["channels"],
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
