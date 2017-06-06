import sublime, sublime_plugin
import subprocess, sys

# TODO(DH): Similar to extract function, use godoctor's extract variable mode.
class ExtractSelectionAsVariable(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()
        print("V")
