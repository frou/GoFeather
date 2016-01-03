![shot]

# Description

I didn't get on with [Sublime Text]'s [Go] package(s) (NIH...?). Here is my own
take on supporting Go in Sublime.

You might like the classifications this package makes for syntax-highlighting
better than the default package's.

There is also basic [integration] of:

## go doc

### Shift+Enter

* With a text selection: Runs `go doc` with the text selection as an argument
and shows the result in an output panel.

* Without a text selection: Runs `go doc` on the package the current source
file is in and shows the result in an output panel.

### Alt+Enter

Shows an input panel and then runs `go doc` with what was submitted as an
argument and shows the result in an output panel.

## godoc.org

### Ctrl+Enter

* With a text selection: Considers the text selection a package path and
launches your web browser showing godoc.org for that package. Surrounding
whitespace and double-quotes are automatically stripped.

* Without a text selection: Launches your web browser showing godoc.org for the
standard library.

# Setup

* Get the package. e.g. on OS X:
`cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/User &&
git clone https://github.com/frou/GoFeather.git`

* Add `"Go"` (the default package) to `"ignored_packages"` in your User
Preferences.

* If you aren't using OS X or want different key bindings, rename or edit the
`.sublime-keymap` file, respectively.

* s/goimports/gofmt/ in the `.sublime-build` file if you don't want to use
`goimports`.

# License

```text
The MIT License

Copyright (c) 2015 Duncan Holm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

[shot]: https://raw.githubusercontent.com/frou/GoFeather/master/screenshot.png
[sublime text]: https://www.sublimetext.com/
[go]: https://www.golang.org/
[integration]: https://github.com/frou/GoFeather/blob/master/document.py
