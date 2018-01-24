#
# This file originated in the repository of the `gocode` daemon (MIT):
#     https://github.com/nsf/gocode/blob/master/subl3/gocode.py
# and has been further developed.
#

import sublime
import sublime_plugin
import subprocess

from .plugin_util import *


class AutocompleteUsingGocode(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("syntax") == "Packages/GoFeather/Go.tmLanguage"

    def on_query_completions(self, prefix, locations):
        cmd = ["gocode", "-f=csv", "autocomplete"]
        view_path = self.view.file_name()
        if view_path:
            cmd.append(view_path)
        cmd.append("c{0}".format(locations[0]))

        gocode_input = self.view.substr(sublime.Region(0, self.view.size()))

        gocode = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=platform_startupinfo())

        gocode_output = gocode.communicate(gocode_input.encode())[0].decode()
        # print(gocode_output)

        result = []
        for line in filter(bool, gocode_output.split("\n")):
            components = line.split(",,")
            result.append(hint_and_replacement(*components))

        return (result, sublime.INHIBIT_WORD_COMPLETIONS)


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
        if s[i] == ',':
            out.append(s[beg:i].strip())
            beg = i + 1
            i += 1
        elif s[i] == '(':
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
    args = split_balanced(sig[beg + 1:end])

    # find the rest of the string, these are returns
    sig = sig[end + 1:].strip()
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
