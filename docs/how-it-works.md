# How it Works
In Shakespeare's work, every line of text has meaning
and communicates volumes beyond the individual words. As such,
`iambic`'s root object is the individual line, or `node`. Each `node`
is assigned a specific `type` based upon simple syntactical rules.
These rules can be broken out into the following logical groups:

## 1. Locales
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
`Act` and may or may not have the structure of a `Scene` or an `Act`.


## 2. Actions and Directions
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


## 3. Personae
The `Persona` object is in its own category and is initially
denoted by a bolded line preceding a block of dialogue. ex:

     **HAMLET**  
     Not so, my lord, I am too much i'th'sun.

Once a persona is created, that object is tracked throughout
the rest of the play.

## 4. Lines
Finally, the meat of the text. Having filtered out all other
syntactical notations, whatever is remaining is considered a
line of `Dialogue`. `Dialogue` objects represent a single
line of spoken word and are grouped within larger `Speech`
objects, which are associated to the character speaking and
nested directly under the `Scene`, `Prologue`, or `Epilogue`
object in which it occurs.

## JSON Schema
The full JSON schema definition is
[hosted on GitHub](https://github.com/seandstewart/iambic/schema.json).
The definition is generated automatically by
[`typical`](https://python-typical.org) and is available as a constant
within the library - `from iambic import SCHEMA`
