![shot]

# Description

I didn't get on with [Sublime Text]'s existing [Go] packages. Here is my take
on a simple, up-to-date package to work with Go in Sublime.

It parses source for syntax-highlighting purposes in a non-hierarchical manner.
You might like the results better than what other packages give.

It defines a Build System around `go (build|install|test|run)` and
`gometalinter`. Files are automatically formatted using `goimports` (falling
back to `gofmt`).

There is also integration of:

## go doc (command-line documentation tool)

### Pressing Alt+Enter:

Shows an input panel which runs `go doc` on what is submitted. The result is
shown in an output panel.

For example, try: `json` or `builtin.make` or `bytes.Buffer.Reset`

### Pressing Shift+Enter:

* With a text selection: Runs `go doc` with the text selection as an argument
and shows the result in an output panel.

* Without a text selection: Runs `go doc` on the directory (package) that the
current Go source file is in and shows the result in an output panel.

## godoc.org & golang.org (web documentation)

### Pressing Ctrl+Enter:

* With a text selection: Considers the text selection a package import path and
launches your web browser showing `godoc.org` for that package. Surrounding
whitespace and double-quotes are automatically stripped.

* Without a text selection: Launches your web browser showing the official
standard library documentation at `golang.org`.

# Installation

* Either

    * Manually get the package. e.g. on macOS:
`cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages &&
git clone https://github.com/frou/GoFeather.git`

    * ...Or install it using `Package Control` by bringing up Sublime's command
palette and running `Package Control: Add Repository` and then pasting in this
repository's URL: `https://github.com/frou/GoFeather`

* Add `"Go"` (the default package that ships with Sublime) to the
`"ignored_packages"` array in Sublime's general User Settings file. This makes
it so that two conflicting packages for the Go language aren't enabled at the
same time.

* (If you additionally want the colour scheme used in the screenshot you can
find it [here][colour])

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
[colour]: https://github.com/frou/Humid
[sublime text]: https://www.sublimetext.com/
[go]: https://www.golang.org/
