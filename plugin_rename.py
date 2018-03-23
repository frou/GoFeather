import sublime
import sublime_plugin

from .util import *


class rename_selected_identifier(sublime_plugin.TextCommand):
    def run(self, args, simulate=False):
        view = self.view
        window = view.window()

        save_and_format(window)

        if not check_num_selections(view, 1):
            return
        sel0 = view.sel()[0]
        # If there is no identifier selected, select the one the cursor is on.
        if sel0.size() == 0:
            window.run_command('find_under_expand')
            sel0 = view.sel()[0]
        selected_text = view.substr(sel0)
        byte_offset = sel0.begin()

        input_label = 'Semantically rename'
        if simulate:
            input_label = 'Simulate semantically renaming'
        input_label += ' "' + selected_text + '" to'

        window.show_input_panel(
            input_label, selected_text,
            lambda name: do_rename(view, byte_offset, name, simulate), None,
            None)
        # Allow immediate type-over in the input panel.
        window.run_command('select_all')


def do_rename(view, byte_offset, new_name, simulate):
    new_name = new_name.strip()
    if new_name == '':
        sublime.status_message('CANNOT RENAME TO EMPTY IDENTIFIER')
        return

    cmd = [
        'gorename',
        # '-v',
        '-offset',
        view.file_name() + ':#' + str(byte_offset),
        '-to',
        new_name
    ]
    if simulate:
        cmd.append('-d')
    cmd_output = run_tool(cmd)
    if not cmd_output:
        simulate = False

    view.window().new_file().run_command("show_refactor_result", {
        "result": cmd_output,
        "is_diff": simulate
    })


class show_refactor_result(sublime_plugin.TextCommand):
    def run(self, edit, result, is_diff):
        view = self.view
        view.set_scratch(True)
        view.set_name("Rename simulation")
        if is_diff:
            view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
        view.insert(edit, 0, result)
