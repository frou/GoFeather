import sublime
import sublime_plugin

from .plugin_util import *


class ExtractSelectionAsFunction(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        save_to_disk(view)

        if not check_num_selections(view, 1):
            return

        sel0 = view.sel()[0]
        if sel0.size() == 0:
            sublime.status_message('SELECTION SHOULD BE NON-EMPTY')
            return

        begin_line, begin_col = view.rowcol(sel0.begin())
        end_line, end_col = view.rowcol(sel0.end())
        # ST uses 0-indexed, godoctor wants 1-indexed
        begin_line = begin_line + 1
        begin_col = begin_col + 1
        end_line = end_line + 1
        end_col = end_col + 1

        window.show_input_panel(
            'Extract selection as function named', '',
            lambda name: do_extraction(view, begin_line, begin_col, end_line, end_col, name),
            None, None)


def do_extraction(view, begin_line, begin_col, end_line, end_col, name):
    name = name.strip()
    if name == '':
        sublime.status_message('FUNCTION NAME CANNOT BE EMPTY')
        return

    cmd = [
        'godoctor', '-file',
        view.file_name(), '-pos',
        '%d,%d:%d,%d' % (begin_line, begin_col, end_line, end_col), '-w',
        'extract', name
    ]
    run_tool(cmd)
    view.sel().clear()
