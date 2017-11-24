import sublime
import sublime_plugin

from .plugin_util import *

# TODO(DH): Document this command in the README.


# Uses: https://godoc.org/golang.org/x/tools/cmd/guru
class QueryGoType(sublime_plugin.TextCommand):
    def run(self, args, simulate=False):
        view = self.view
        window = view.window()

        save_to_disk(view)

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
