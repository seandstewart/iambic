## Parsing Text
`iambic` relies upon a set of standard style tokens for parsing text. For an in-depth
breakdown of what each detected node means, check out
[How It Works](../how-it-works.md). The final product of parsing a play is a single
`Play` object, which is *hashable and immutable*.

## Tokens

### Headings
Act, Scene, Epilogue, Prologue, and Intermission sections should be
wrapped in heading tokens. (`#...` for Markdown,
`<h(1-...)>...</h(1-...)>` for HTML). i.e.:

    ## ACT I
    
    <h1>ACT I</h1>
    
    ## SCENE II. The same.
    
    <h2>SCENE II. The same.</h2>



### Bolded
**Bolded Text** is significant, and is considered a character name,
i.e.:

    **HAMLET**
    
    <b>HAMLET</b>
    
    **First Soldier**
    
    <b>First Soldier</b>

### Italics
_Italicized text_ is also significant - it signals that everything
enclosed within the block is a character action or stage direction.
`iambic` will mark any italicized text that is also enclosed within
brackets as stage actions and associate the action to the last-seen
character when building the tree.

    // Stage 'Direction'
    _Alarum._
    *Alarum.*
    <i>Alarum.</i>
    
    // Character 'Action'
    _\[Aside]_
    *[Aside]*
    <i>[Aside]</i>

As a bonus, `iambic` also attempts to detect

Multi-line blocks are also supported, as in plain markdown.


### Ellipsis or Hanging & Leading "/"
Ellipses (either `…` or `...`) or a Hanging & Leading "/" indicate the beginning and end
of a "shared" line of poetry, i.e.:

    **MALCOLM**
    Say to the king the knowledge of the broil  
    As thou didst leave it. ...
    
    **Sergeant**  
    ... Doubtful it stood;  
    As two spent swimmers, that do cling together  

Or:

    **MALCOLM**
    Say to the king the knowledge of the broil  
    As thou didst leave it. /
    
    **Sergeant**  
    / Doubtful it stood;  
    As two spent swimmers, that do cling together  


`As thou didst leave it. / / Doubtful it stood;` scan as a single line of iambic
pentameter. The `/` at the end of a line will signal to `iambic` that we are now
entering a continuation of the same poetic line. `iambic` will track the continuation
until the next line fails to start or end with a `/`. As a bonus, when `iambic`
re-renders this text, it will auto-indent the lines with a non-breaking space, like so:

    **MALCOLM**
    Say to the king the knowledge of the broil  
    As thou didst leave it. /
    
    **Sergeant**  
                            / Doubtful it stood;  
    As two spent swimmers, that do cling together  

`iambic` will also track the owner of every shared line and increment their own count of
spoken lines. This will not, however, increment the total number of lines in a given
play. `iambic` will not increment again until it detects it has exited the continuation.


### All Other Text
Any non-tokenized text will be marked as a single line of dialogue and
associated to the last character seen.


## Examples

```
>>> import iambic
>>> play = """
... ## ACT I
... ## SCENE I. A field.
...
... _Enter FOO from one side, BAR from another._
...
... **FOO**
... Bar. /
...
... **BAR**
... / Foo!
...
... _Exeunt, severally_
... """
...
>>> parsed = iambic.parse.text(play, title="Foo")
>>> print(parsed.tojson(indent=2))
{
  "type": "play",
  "body": [
    {
      "type": "act",
      "index": 0,
      "text": "ACT I",
      "num": 1,
      "body": [
        {
          "type": "scene",
          "index": 1,
          "text": "SCENE I",
          "num": 1,
          "setting": "A field.",
          "act": "act-i",
          "body": [
            {
              "type": "entrance",
              "index": 2,
              "text": "Enter FOO from one side, BAR from another.",
              "scene": "act-i-scene-i-i",
              "personae": [
                "foo",
                "bar"
              ]
            },
            {
              "type": "speech",
              "persona": "foo",
              "scene": "act-i-scene-i-i",
              "body": [
                {
                  "type": "dialogue",
                  "line": "Bar. \/",
                  "persona": "foo",
                  "scene": "act-i-scene-i-i",
                  "index": 4,
                  "lineno": 1,
                  "linepart": 1
                }
              ],
              "index": 4
            },
            {
              "type": "speech",
              "persona": "bar",
              "scene": "act-i-scene-i-i",
              "body": [
                {
                  "type": "dialogue",
                  "line": "\/ Foo!",
                  "persona": "bar",
                  "scene": "act-i-scene-i-i",
                  "index": 6,
                  "lineno": 1,
                  "linepart": 2
                }
              ],
              "index": 6
            },
            {
              "type": "exit",
              "index": 7,
              "text": "Exeunt, severally",
              "scene": "act-i-scene-i-i",
              "personae": [
              ]
            }
          ],
          "personae": [
            "foo",
            "bar"
          ]
        }
      ]
    }
  ],
  "personae": [
    {
      "type": "persona",
      "index": 3,
      "text": "FOO",
      "name": "Foo",
      "short": null
    },
    {
      "type": "persona",
      "index": 5,
      "text": "BAR",
      "name": "Bar",
      "short": null
    }
  ],
  "meta": {
    "type": "meta",
    "rights": "Creative Commons Non-Commercial Share Alike 3.0",
    "language": "en-GB-emodeng",
    "publisher": "Published w\/ ❤️ using iambic - https:\/\/pypi.org\/project\/iambic",
    "title": null,
    "subtitle": null,
    "edition": 1,
    "author": "William Shakespeare",
    "editors": [
    ],
    "tags": [
    ]
  }
}
```


## Parsing JSON
Iambic is equipped to load valid JSON documents into the ast. For
instance:

```
>>> iambic.parse.data("""{
...      "type":"persona",
...      "index":3,
...      "text":"FOO",
...      "name":"Foo",
...      "short":null
...    }""")
Persona(index=3, text='FOO', name='Foo', short=None)
```

Nested data is also handled without any additional work.
