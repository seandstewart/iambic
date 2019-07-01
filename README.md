iambic: Data extraction and rendering library for Shakespearean text. :scroll: 
==============================================================================
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


## How it works
In Shakespeare's work, every line of text has meaning and 
communicates volumes beyond the individual words. As such,
`iambic`'s root object is the individual line, or `node`.
Each `node` is assigned a specific `type` based upon simple
syntactical rules. These rules can be broken out into the
following logical groups:

### 1. Locales
A `Locale` will be denoted by header formatting (H1-5) and 
represents a logical break in the forward action of the
play. These can be thought of as the entries that may show
up in a Table of Contents, and can include:
- `Act`
- `Scene`
- `Prologue` or `Epilogue`

An `Act` may have many nested `Scene`, `Prologue`, and
`Epilogue` sections.

A `Scene` will be always be nested under an act `Act`. A
`Scene` contains speeches, dialogue, and actions.

A `Prologue` or `Epilogue` may or may not be nested under an
`Act`, but have the same internal structure as a `Scene`.


### 2. Actions and Directions
Actions and Directions will be denoted by an _italicized_ 
paragraph of any length and represent a physical action that
takes place on stage. These can include:
- Character Action (`Action`)
- Stage Direction (`Direction`)
- Entrance/Exit (`Entrance` or `Exit`)

An `Action` object represents an action of a specific
character and are usually found within or just after a
speech. If these are more than one word (such as *Aside*),
they will either reference the character by pronoun, or
begin with *To ...*. In order for `iambic` to understand
that the given paragraph is an `Action`, the paragraph
should be wrapped in brackets (`[]`) in addition to
italicized. ex: *\[He brandishes his sword]*, *\[To
JULIET]*).

A `Direction` is more straightforward - it is simply a stage
direction, meaning a paragraph of text which illucidates
some on-stage action between any number of characters. A
`Direction` will always be written in third-person
omniscient and reference characters by name and be denoted
simply by italics. ex: *Flourish*, *They fight*, *HAMLET
stabs CLAUDIUS*.  

An `Entrance` or `Exit` will usually lead or finish with
`Enter`, `Exit`, or `Exeunt` and be italicized.


### 3. Personae
The `Persona` object is in its own category and is initially
denoted by a bolded line preceding a block of dialogue. ex:

 **HAMLET**  
 Not so, my lord, I am too much i'th'sun.

Once a persona is created, that object is tracked throughout
the rest of the play.

### 4. Lines
Finally, the meat of the text. Having filtered out all other
syntactical notations, whatever is remaining is considered a
line of `Dialogue`. `Dialogue` objects represent a single
line of spoken word and are grouped within larger `Speech`
objects, which are associated to the character speaking and
nested directly under the `Scene`, `Prologue`, or `Epilogue`
object in which it occurs.

## The Schema
The full schema specification has been written in JSON
Schema 7.0 and can be found
[here](iambic/schema/schema.json)

## Documentation

Full documentation coming soon!


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
