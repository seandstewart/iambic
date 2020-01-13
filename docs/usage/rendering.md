# Rendering Parsed Text
Once your text is parsed, iambic provides an HTML renderer which
provides a fully-qualified HTML document with unique selectors, data-*
fields for custom JS, and a TOC tree rendered in a nave component:


## Rendering to HTML

Calling `iambic.render.html(<parsed>)` will result in:

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <title></title>
    <meta name="language" content="en-GB-emodeng" />
    <meta name="publisher" content="Published w/ ❤️ using iambic - https://pypi.org/project/iambic" />
    <meta name="rights" content="Creative Commons Non-Commercial Share Alike 3.0" />
    <meta name="author" content="William Shakespeare" />
    <meta name="edition" content="1" />
    <meta name="editors" content="" />
    <meta name="keywords" content="" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  </head>
  <body>
    <nav class="table-of-contents" id="none-table-of-contents" role="navigation">
      <h2>Table of Contents</h2>
      <ol>
        <li>
          <a href="#act-i">ACT I</a>
          <ol>
            <li>
              <a href="#act-i-scene-i">SCENE I</a>
            </li>
          </ol>
        </li>
      </ol>
    </nav>
    <h2 class="act" id="act-i" data-index="0">ACT I</h2>
    <h3 class="scene" id="act-i-scene-i" data-index="1">SCENE I</h3>
    <p class="entrance" id="act-i-scene-i-entrance-2">
      <em data-index="2">Enter FOO from one side, BAR from another.</em>
    </p>
    <p class="speech" id="act-i-scene-i-foo-speech-1-1">
      <strong class="persona" id="foo-act-i-scene-i-foo-speech-1-1">Foo</strong>
      <br />
      <span class="dialogue" id="foo-dialogue-1-1" data-index="4" data-lineno="1">Bar. ...<br /></span>
    </p>
    <p class="speech" id="act-i-scene-i-bar-speech-1-1">
      <strong class="persona" id="bar-act-i-scene-i-bar-speech-1-1">Bar</strong>
      <br />
      <span class="dialogue" id="bar-dialogue-1-2" data-index="6" data-lineno="1">... Foo!<br /></span>
    </p>
    <p class="exit" id="act-i-scene-i-exit-7">
      <em data-index="7">Exeunt, severally</em>
    </p>
  </body>
</html>
```

## Rendering to JSON

One may also make use of the `iambic.render.json` function, but this
is merely provided for API-completeness. All Iambic objects have a
`json` property for pretty-printing JSON which this function uses
under the hood.
