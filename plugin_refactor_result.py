import sublime
import sublime_plugin

from .plugin_common import *


class ShowRefactorResult(sublime_plugin.TextCommand):
    def run(self, edit, result, is_diff):
        view = self.view
        view.set_scratch(True)
        if is_diff:
            view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
        view.insert(edit, 0, result)
