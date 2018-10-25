#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="yet-another-io-channels-library",
    version="0.2.0",
    author="Ilya Konovalov",
    author_email="aragaer@gmail.com",
    description="Simple IO channels library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="socket pipe",
    url="https://github.com/aragaer/channels",
    packages=["channels"],
    platforms=["UNIX"],
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
