iambic: Data extraction and rendering library for Shakespearean text. :scroll: 
==============================================================================
[![image](https://img.shields.io/pypi/v/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/pypi/l/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/pypi/pyversions/iambic.svg)](https://pypi.org/project/iambic/)
[![image](https://img.shields.io/github/languages/code-size/seandstewart/iambic.svg?style=flat)](https://github.com/seandstewart/iambic)
[![image](https://img.shields.io/travis/seandstewart/iambic.svg)](https://travis-ci.org/seandstewart/iambic)
[![codecov](https://codecov.io/gh/seandstewart/iambic/branch/master/graph/badge.svg)](https://codecov.io/gh/seandstewart/iambic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Netlify Status](https://api.netlify.com/api/v1/badges/91ace14b-e26e-4026-ac5c-3e5640f2910f/deploy-status)](https://app.netlify.com/sites/iambic/deploys)

Let computers do the hard work for you! `iambic` provides:
1. The most accurate method for counting lines automatically.
2. Automatically track which characters are speaking in any scene.
3. Deterministic, repeatable results, with the ability to store your
   data as JSON with strictly defined schema for passing over the wire
   or storing locally or in a NoSQL database between runtimes.


## Installation

In order to install the latest version, simply `pip3 install
-U iambic`.

This library requires Python 3.7 or greater.


## What is it?
`iambic` was originally envisioned as a tool for translating
Shakespearean text into actionable information, i.e.:
1. How many lines are in this particular play?
2. How many lines does a given character speak in this play?
3. Which characters speak, in which scenes and acts?

As a result of the implementation, this tool can be applied 
to any body of text which adhere's to its parsing syntax.


## The Schema
The full schema specification has been written in JSON
Schema 7.0 and can be found
[here](schema.json)

## Documentation

The full documentation is available at
[iambic.seandstewart.io](https://iambic.seandstewart.io)


## How to Contribute
1.  Check for open issues or open a fresh issue to start a 
    discussion around a feature idea or a bug.
2.  Create a branch on Github for your issue or fork
    [the repository](https://github.com/seandstewart/iambic)
    on GitHub to start making your changes to the **master**
    branch.
3.  Write a test which shows that the bug was fixed or that 
    the feature works as expected.
4.  Send a pull request and bug the maintainer until it gets
     merged and published. :)
