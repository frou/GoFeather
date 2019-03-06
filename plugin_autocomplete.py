#
# This file originated in the repository of the `gocode` daemon (MIT):
#     https://github.com/nsf/gocode/blob/master/subl3/gocode.py
# and has been further developed.
#

import sublime
import sublime_plugin
import subprocess

from .util import *

# TODU(DH): Did I write stuff that is now obsoleted by this PR? https://github.com/mdempsky/gocode/pull/91

# TODU(DH): Port additional changes from guy's async completions work:
# https://github.com/nsf/gocode/pull/531#issuecomment-445950433
# https://github.com/stamblerre/gocode/pull/15

class AutocompleteUsingGocode(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return settings_indicate_go(settings)

    def __init__(self, view):
        super().__init__(view)
        self._running = False
        self._completions = None
        self._location = 0
        self._prefix = ""

    def fetch_query_completions(self, prefix, location):
        self._running = True
        self._location = location

        # TODU(DH): Use -source flag so that it's not built packages being inspected? https://github.com/mdempsky/gocode/commit/7282f446b501b064690f39640b70e1ef54806c60
        # TODU(DH): Will -source be usably performant when this is merged? https://github.com/mdempsky/gocode/issues/28
        cmd = ["gocode", "-f=csv", "-builtin", "-unimported-packages", "autocomplete"]
        view_path = self.view.file_name()
        if view_path:
            cmd.append(view_path)
        cmd.append("c{0}".format(location))

        gocode_input = self.view.substr(sublime.Region(0, self.view.size()))

        gocode = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=platform_startupinfo(),
        )

        gocode_output = gocode.communicate(gocode_input.encode())[0].decode()
        # print(gocode_output)

        result = []
        for line in filter(bool, gocode_output.split("\n")):
            components = line.split(",,")
            result.append(
                hint_and_replacement(components[0], components[1], components[2])
            )

        # Exit conditions:
        if len(result) == 0:
            return

        if self._prefix != prefix:
            return

        # Check if this query completions request is for the "latest" location
        if self._location != location:
            return

        self._completions = result
        self._running = False

        self.open_query_completions()

    def open_query_completions(self):
        self.view.run_command("hide_auto_complete")
        sublime.set_timeout(lambda: self.view.run_command("auto_complete"))

    def on_query_completions(self, prefix, locations):
        loc = locations[0]

        # Return this to cause Sublime to not even attempt to offer ANY kind of completions at this time.
        dont_complete = (
            [],
            sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
        )

        if self._completions:
            completions = self._completions

            self._completions = None
            self._prefix = ""

            return (completions, sublime.INHIBIT_WORD_COMPLETIONS)

        if self._running and len(prefix) != 0:
            return dont_complete

        self._prefix = prefix

        sublime.set_timeout_async(lambda: self.fetch_query_completions(prefix, loc))

        return dont_complete


# go to balanced pair, e.g.:
# ((abc(def)))
# ^
# \--------->^
#
# returns -1 on failure
def skip_to_balanced_pair(str, i, open, close):
    count = 1
    i += 1
    while i < len(str):
        if str[i] == open:
            count += 1
        elif str[i] == close:
            count -= 1

        if count == 0:
            break
        i += 1
    if i >= len(str):
        return -1
    return i


# split balanced parens string using comma as separator
# e.g.: "ab, (1, 2), cd" -> ["ab", "(1, 2)", "cd"]
# filters out empty strings
def split_balanced(s):
    out = []
    i = 0
    beg = 0
    while i < len(s):
        if s[i] == ",":
            out.append(s[beg:i].strip())
            beg = i + 1
            i += 1
        elif s[i] == "(":
            i = skip_to_balanced_pair(s, i, "(", ")")
            if i == -1:
                i = len(s)
        else:
            i += 1

    out.append(s[beg:i].strip())
    return list(filter(bool, out))


def extract_arguments_and_returns(sig):
    sig = sig.strip()
    if not sig.startswith("func"):
        return [], []

    # find first pair of parens, these are arguments
    beg = sig.find("(")
    if beg == -1:
        return [], []
    end = skip_to_balanced_pair(sig, beg, "(", ")")
    if end == -1:
        return [], []
    args = split_balanced(sig[beg + 1 : end])

    # find the rest of the string, these are returns
    sig = sig[end + 1 :].strip()
    sig = sig[1:-1] if sig.startswith("(") and sig.endswith(")") else sig
    returns = split_balanced(sig)

    return args, returns


# takes gocode's candidate and returns sublime's hint and replacement
def hint_and_replacement(category, name, go_type):
    hint = category.ljust(7) + " " + name
    replacement = name
    if category == "func":
        args, returns = extract_arguments_and_returns(go_type)
        if args:
            hint += " (…)"
            sargs = []
            for i, a in enumerate(args):
                ea = a.replace("{", "\\{").replace("}", "\\}")
                sargs.append("${{{0}:{1}}}".format(i + 1, ea))
            replacement += "(" + ", ".join(sargs) + ")"
        else:
            hint += " ()"
            # Have the () itself be a snippet, to normalise the number of
            # keyboard interactions to deal with the argument list. i.e. no
            # matter the number of arguments, at least one tab press is
            # required to advance beyond it.
            replacement += "${1:()}"
        if returns:
            if len(returns) > 0:
                hint += "\t" + ", ".join(returns)
    else:
        hint += "\t" + go_type
    return hint, replacement


# TODO(DH): Completion snippet emitted for a variadic function parameter should be nested. Because a variadic function parameter can be satisfied by zero arguments, the snippet emitted should be a snippet within a snippet so that the entire thing can be deleted by pressing backspace/delete just once. i.e. initially `, a ...interface{}` will be selected, and *if* tab is then pressed, just `a ...interface{}` will selected.
