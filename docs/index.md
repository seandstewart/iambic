iambic: Data extraction and rendering library for Shakespearean text. :scroll: 
[![image](https://img.shields.io/pypi/v/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/pypi/l/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/pypi/pyversions/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/github/languages/code-size/seandstewart/iambic.svg?style=flat)](https://github.com/seandstewart/iambic)
[![image](https://img.shields.io/travis/seandstewart/iambic.svg)](https://travis-ci.org/seandstewart/iambic)
[![codecov](https://codecov.io/gh/seandstewart/iambic/branch/master/graph/badge.svg)](https://codecov.io/gh/seandstewart/iambic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Let computers do the hard work for you! `iambic` provides:

1. The most accurate method for counting lines automatically.
2. Automatically track which characters are speaking in any scene.
3. Deterministic, repeatable results, with the ability to store your
   data as JSON with strictly defined schema for passing over the wire
   or storing locally or in a NoSQL database between runtimes.


## Installation

In order to install the latest version, simply `pip3 install
-U iambic`.

This library requires Python 3.6 or greater.


## What is it?
`iambic` was originally envisioned as a tool for translating
Shakespearean text into actionable information, i.e.:

1. How many lines are in this particular play?
2. How many lines does a given character speak in this play?
3. Which characters speak, in which scenes and acts?

As a result of the implementation, this tool can be applied 
to any body of text which adhere's to its parsing syntax.
