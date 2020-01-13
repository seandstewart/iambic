# Generating Breakdowns
One of the best things about the library is its ability to quickly
generate a tabular mapping of every character and their presence in
the play. 

```
>>> import iambic
>>> import json
>>> play = """
... ## ACT I
... ## SCENE I. A field.
...
... _Enter FOO from one side, BAR from another._
...
... **FOO**
... Bar. ...
...
... **BAR**
... ... Foo!
...
... _Exeunt, severally_
... """
...
>>> parsed = iambic.parse.text(play, title="Foo")
>>> print(iambic.render.table(parsed))
Dramatis Personae|First Appearance|Lines|I.i
-----------------|----------------|-----|---
Foo              |3               |1    |X  
Bar              |5               |1    |X  
```

As the complexity of the play grows--such as with the Henrys--this
resource is invaluable for maintaining a high-level look at where and
how characters interact.
