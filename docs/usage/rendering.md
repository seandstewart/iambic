# Rendering Parsed Text
Once your text is parsed, iambic provides a renderer which will take a parsed play and
re-render the markdown with additional metadata in-line. Iambic makes use of the
Python-Markdown library and its suite of extensions to support rendering this markdown
to HTML.

## Rendering to Markdown

To extend from the example given in [Parsing](parsing.md):

```
>>> print(iambic.render.markdown(parsed))
## Overview

???+ "High-Level Stats"
    **Total Lines:** 1  
    **Total Characters:** 2  
    **Total Scenes:** 1  

???+ "Publication Information"
    **Rights:** Creative Commons Non-Commercial Share Alike 3.0  
    **Language:** en-GB-emodeng  
    **Publisher:** Published w/ ❤️ using iambic - https://pypi.org/project/iambic  
    **Edition:** 1  
    **Author:** William Shakespeare  

## Index

???+ "Character Navigation"
    === "I: i"
        - [Foo ⇒ 💬](#act-i-scene-i-i-foo-speech-1-1-4)
        - [Bar ⇒ 💬](#act-i-scene-i-i-bar-speech-1-1-6)

??? "Character Navigation (Grid)"
    | Dramatis Personae   |   First Appearance |   Lines | I: i                                    |
    |---------------------|--------------------|---------|-----------------------------------------|
    | Foo                 |                  3 |       1 | [💬](#act-i-scene-i-i-foo-speech-1-1-4) |
    | Bar                 |                  5 |       1 | [💬](#act-i-scene-i-i-bar-speech-1-1-6) |

??? "Dramatis Personae"
    === "Order of Appearance"
        - Foo (1 lines)
        - Bar (1 lines)
    === "Number of Lines"
        - Foo (1 lines)
        - Bar (1 lines)

## ACT I {: id=act-i }

### SCENE I. A field. {: id=act-i-scene-i-i }

*Enter FOO from one side, BAR from another.* <a class="headerlink" href="#act-i-scene-i-i-entrance-2" title="Permanent link">👁️‍🗨️</a>
{: id=act-i-scene-i-i-entrance-2 }

**Foo** <a class="headerlink" href="#act-i-scene-i-i-foo-speech-1-1-4" title="Permanent link">(1, 1)</a>  
Bar. /  
{: id=act-i-scene-i-i-foo-speech-1-1-4 }

**Bar** <a class="headerlink" href="#act-i-scene-i-i-bar-speech-1-1-6" title="Permanent link">(1, 1)</a>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/ Foo!  
{: id=act-i-scene-i-i-bar-speech-1-1-6 }

*Exeunt, severally* <a class="headerlink" href="#act-i-scene-i-i-exit-7" title="Permanent link">👁️‍🗨️</a>
{: id=act-i-scene-i-i-exit-7 }
```


## Rendering to HTML

Finally, to get fully-rendered HTML, you may do the following:

```
>>> print(iambic.render.html(parsed))
<h2>Overview</h2>
<details open="open"><summary>High-Level Stats</summary><p><strong>Total Lines:</strong> 1<br />
<strong>Total Characters:</strong> 2<br />
<strong>Total Scenes:</strong> 1  </p>
</details>
<details open="open"><summary>Publication Information</summary><p><strong>Rights:</strong> Creative Commons Non-Commercial Share Alike 3.0<br />
<strong>Language:</strong> en-GB-emodeng<br />
<strong>Publisher:</strong> Published w/ ❤️ using iambic - https://pypi.org/project/iambic<br />
<strong>Edition:</strong> 1<br />
<strong>Author:</strong> William Shakespeare  </p>
</details>
<h2>Index</h2>
<details open="open"><summary>Character Navigation</summary><div class="tabbed-set" data-tabs="1:1"><input checked="checked" id="__tabbed_1_1" name="__tabbed_1" type="radio" /><label for="__tabbed_1_1">I: i</label><div class="tabbed-content">
<ul>
<li><a href="#act-i-scene-i-i-foo-speech-1-1-4">Foo ⇒ 💬</a></li>
<li><a href="#act-i-scene-i-i-bar-speech-1-1-6">Bar ⇒ 💬</a></li>
</ul>
</div>
</div>
</details>
<details><summary>Character Navigation (Grid)</summary><table>
<thead>
<tr>
<th>Dramatis Personae</th>
<th>First Appearance</th>
<th>Lines</th>
<th>I: i</th>
</tr>
</thead>
<tbody>
<tr>
<td>Foo</td>
<td>3</td>
<td>1</td>
<td><a href="#act-i-scene-i-i-foo-speech-1-1-4">💬</a></td>
</tr>
<tr>
<td>Bar</td>
<td>5</td>
<td>1</td>
<td><a href="#act-i-scene-i-i-bar-speech-1-1-6">💬</a></td>
</tr>
</tbody>
</table>
</details>
<details><summary>Dramatis Personae</summary><div class="tabbed-set" data-tabs="2:2"><input checked="checked" id="__tabbed_2_1" name="__tabbed_2" type="radio" /><label for="__tabbed_2_1">Order of Appearance</label><div class="tabbed-content">
<ul>
<li>Foo (1 lines)</li>
<li>Bar (1 lines)</li>
</ul>
</div>
<input id="__tabbed_2_2" name="__tabbed_2" type="radio" /><label for="__tabbed_2_2">Number of Lines</label><div class="tabbed-content">
<ul>
<li>Foo (1 lines)</li>
<li>Bar (1 lines)</li>
</ul>
</div>
</div>
</details>
<h2 id="act-i">ACT I</h2>
<h3 id="act-i-scene-i-i">SCENE I. A field.</h3>
<p id="act-i-scene-i-i-entrance-2"><em>Enter FOO from one side, BAR from another.</em> <a class="headerlink" href="#act-i-scene-i-i-entrance-2" title="Permanent link">👁️‍🗨️</a></p>
<p id="act-i-scene-i-i-foo-speech-1-1-4"><strong>Foo</strong> <a class="headerlink" href="#act-i-scene-i-i-foo-speech-1-1-4" title="Permanent link">(1, 1)</a><br />
Bar. /<br /></p>
<p id="act-i-scene-i-i-bar-speech-1-1-6"><strong>Bar</strong> <a class="headerlink" href="#act-i-scene-i-i-bar-speech-1-1-6" title="Permanent link">(1, 1)</a><br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/ Foo!<br /></p>
<p id="act-i-scene-i-i-exit-7"><em>Exeunt, severally</em> <a class="headerlink" href="#act-i-scene-i-i-exit-7" title="Permanent link">👁️‍🗨️</a></p>

```

## Rendering to JSON

One may also make use of the `iambic.render.json` function, but this
is merely provided for API-completeness. All Iambic objects have a
`tojson()` method for pretty-printing JSON which this function uses
under the hood.
