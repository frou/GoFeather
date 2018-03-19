import sublime
import sublime_plugin
import os
import sys

# TODO(DH): Make use of check_num_selections too.
from .util import *


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

    show_doc(window, get_doc(cmd_wd, cmd_arg))


def get_doc(cmd_wd, cmd_arg):
    # `go doc` (Go 1.5+) has different capabilities to `godoc`.
    cmd = [
        'go',
        'doc',
        '-c',
    ]
    if cmd_arg:
        # Most of the interesting identifiers in the pseudo-package builtin are
        # considered unexported because they start with lowercase.
        if cmd_arg == 'builtin' or cmd_arg.startswith('builtin.'):
            cmd.append('-u')
        cmd.append(cmd_arg)
    try:
        cmd_output = run_tool(cmd, wd=cmd_wd)
        if cmd_output:
            return cmd_output.decode('utf-8')
    except:
        pass

    sublime.status_message('FAILED: ' + ' '.join(cmd))
    return None

def show_doc(window, doc):
    panel_name_suffix = 'show_go_doc'
    panel_name_full = 'output.' + panel_name_suffix
    if doc is None:
        if window.active_panel() == panel_name_full:
            window.run_command("hide_panel")
        return
    output = window.create_output_panel(panel_name_suffix)
    output.run_command('append', {'characters': doc})
    window.run_command('show_panel', {'panel': panel_name_full})


class quick_show_go_doc_from_view(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        if len([sl for sl in view.sel() if not sl.empty()]) != 0:
            sublime.status_message('TOO MANY SELECTIONS')
            return

        # TODO(DH): get save_and_format(window) working well here.

        # Select the current word plus the character before it.
        view.run_command('move', {'by': 'wordends', 'forward': True})
        view.run_command('move',
                         {'by': 'words',
                          'forward': False,
                          'extend': True})

        # Is the character before the current word a dot?

        view.run_command(
            'move', {'by': 'characters',
                     'forward': False,
                     'extend': True})

        provisional_sel_str = view.substr(view.sel()[0])

        if provisional_sel_str.startswith('.'):
            # Yes: Extend the selection to cover the word before the dot too.
            view.run_command('move',
                             {'by': 'words',
                              'forward': False,
                              'extend': True})
        else:
            # No: Don't have the dot selected any more.
            view.run_command(
                'move', {'by': 'characters',
                         'forward': True,
                         'extend': True})

        adjusted_sel = view.sel()[0]
        adjusted_sel_str = view.substr(adjusted_sel)

        # ------------------------------------------------------------

        byte_offset = adjusted_sel.begin()
        guru_cmd = [
            'guru', '-json', 'describe',
            view.file_name() + ':#' + str(byte_offset)
        ]
        guru_cmd_output = run_tool(guru_cmd)
        if guru_cmd_output:
            # print(guru_cmd)
            json_obj = sublime.decode_value(guru_cmd_output.decode('utf-8'))

            desc_str = json_obj['desc']
            if desc_str == "identifier":
                type_str = json_obj['value']['type']
                # *os.File -> os.File
                type_str = type_str.lstrip("*")
                if "." in adjusted_sel_str:
                    # f.Close -> os.File.Close
                    adjusted_sel_str = "%s.%s" % (type_str, adjusted_sel_str.split(".")[1])
                elif not type_str.startswith("func("):
                    adjusted_sel_str = type_str

        cmd_wd, _ = determine_wd_for_cmd(view)
        show_doc(
            window,
            get_doc(cmd_wd, adjusted_sel_str))

        # End up with the caret at the start of the word it was initially in, and with no selection.
        view.run_command('move', {'by': 'characters', 'forward': True})
        view.run_command('move',
                         {'by': 'words',
                          'forward': False,
                          'extend': False})


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
