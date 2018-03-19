import sublime
import sublime_plugin

from .util import *

# TODO(DH): The _shows_docs plugin can get the doc for e.g. a package-qualified identifier. What about getting the doc for a method/field that is preceded by a variable name rather than a package name?
# This can currently be approximated with:
# (cursor on variable)
# Shift+F9
# (manuallly adding `.MethodName` as a suffix in the input panel)
# Return
#
# QueryGoType could be removed? Then QuickShowGoDocFromView could be updated to
# assume the prefix is a package name, then, if that fails, assume the prefix
# is a variable name, lookup its type, then synthesize a second
# ShowGoDocFromView/QuickShowGoDocFromView.

class QueryGoType(sublime_plugin.TextCommand):
    def run(self, args, simulate=False):
        view = self.view
        window = view.window()

        save_and_format(window)

        if not check_num_selections(view, 1):
            return
        byte_offset = view.sel()[0].begin()

        cmd = [
            'guru', '-json', 'describe',
            view.file_name() + ':#' + str(byte_offset)
        ]
        cmd_output = run_tool(cmd)
        if not cmd_output:
            return

        json_obj = sublime.decode_value(cmd_output.decode('utf-8'))
        type_str = json_obj['value']['type']

        window.settings().set(SettingsKeys.PANEL_QUERIED_TYPE, type_str)
        window.run_command('show_go_doc_from_panel')
        window.settings().erase(SettingsKeys.PANEL_QUERIED_TYPE)
