import sublime
import sublime_plugin
import os
import sys

# TODO(DH): Make use of check_num_selections too.
from .util import *

# TODO(DH): Have a toggle-able model where simply clicking to place the caret automatically queries docs for that position.

def determine_wd_for_cmd(view):
    view_fs_path = view.file_name()
    if view_fs_path:
        cmd_wd = os.path.dirname(view_fs_path)
        cmd_wd_is_go_pkg = True
    else:
        cmd_wd = os.getcwd()
        cmd_wd_is_go_pkg = False
    return (cmd_wd, cmd_wd_is_go_pkg)


def submit_panel(window, cmd_wd, cmd_wd_is_go_pkg, s, save_for_replay):
    if save_for_replay:
        window.settings().set(SettingsKeys.PANEL_LAST_USER_INPUT, s)
    s = s.strip()
    cmd_arg = None if s == '' else s

    if not cmd_arg and not cmd_wd_is_go_pkg:
        sublime.status_message('NOT IN A GO PACKAGE')
        return

    show_gofeather_output_panel(window, get_doc(cmd_wd, cmd_arg))


def get_doc(cmd_wd, cmd_arg):
    # `go doc` (Go 1.5+) has different capabilities to `godoc`.
    cmd = [
        'go',
        'doc',
        # Don't suppress documentation for `main` packages.
        '-cmd',
        # Symbol matching honors case (paths not affected).
        '-c',
        # Show unexported symbols as well as exported.
        '-u'
    ]
    if cmd_arg:
        cmd.append(cmd_arg)

    # print(cmd)
    cmd_output = run_tool(cmd, wd=cmd_wd)
    if cmd_output:
        return cmd_output
    else:
        return None

class quick_show_go_doc_from_view(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        if len([sl for sl in view.sel() if not sl.empty()]) != 0:
            sublime.status_message('TOO MANY SELECTIONS')
            return

        # TODO(DH): Possibly feed in unsaved file(s) rather than saving? https://github.com/zmb3/gogetdoc#unsaved-files
        save_if_needed(view)

        byte_offset = view.sel()[0].begin()
        gogetdoc_cmd = [
            # '-u',
            'gogetdoc', '-pos', "%s:#%d" % (view.file_name(), byte_offset)
        ]
        show_gofeather_output_panel(window, run_tool(gogetdoc_cmd))


class show_go_doc_from_panel(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = window.active_view()

        cmd_wd, cmd_wd_is_go_pkg = determine_wd_for_cmd(view)

        label = 'Document'
        placeholder = window.settings().get(SettingsKeys.PANEL_LAST_USER_INPUT,
                                            '')
        is_written_input = True

        type_str = window.settings().get(SettingsKeys.PANEL_QUERIED_TYPE, None)
        if type_str:
            placeholder = type_str
            is_written_input = False

        window.show_input_panel(
            label, placeholder,
            lambda s: submit_panel(window, cmd_wd, cmd_wd_is_go_pkg, s, is_written_input),
            None, None)
        # Allow immediate type-over in the input panel.
        window.run_command('select_all')


class launch_browser_docs_from_view(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        # Show the stdlib documentation on the official site?
        default_docs = False
        non_empty_selections = [sl for sl in view.sel() if not sl.empty()]
        if len(non_empty_selections) == 0:
            default_docs = True
        if len(non_empty_selections) == 1:
            pkg = view.substr(non_empty_selections[0])
            pkg = pkg.strip(' \t\r\n"')
        elif len(non_empty_selections) > 1:
            sublime.status_message('TOO MANY SELECTIONS')
            return
        launcher = 'xdg-open'
        via_shell = False
        if sys.platform == 'darwin':
            launcher = 'open'
        elif sys.platform == 'win32':
            launcher = 'start'
            via_shell=True
        if default_docs:
            run_tool([launcher, 'https://golang.org/pkg/'], wd='.', shell=via_shell)
        else:
            run_tool([launcher, 'https://godoc.org/' + pkg.lower()], wd='.', shell=via_shell)

# class guru_info(sublime_plugin.TextCommand):
#     def run(self, args):
#         view = self.view
#         sel0 = view.sel()[0]

#         file_path = view.file_name()
#         byte_offset = sel0.begin()

#         guru_cmd = [
#             'guru', '-json', 'describe', "%s:#%d" %(file_path, byte_offset)
#         ]
#         guru_cmd_output = run_tool(guru_cmd)
#         print(sublime.decode_value(guru_cmd_output))
