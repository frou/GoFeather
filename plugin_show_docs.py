import sublime, sublime_plugin
import os, subprocess, sys

# TODO(DH): Use the .plugin_util functionality in here too.

# This plugin uses `go doc` (Go 1.5+) which is different from `godoc`.

unique_settings_prefix = 'go_doc_'
settings_key_panel_replay = unique_settings_prefix + 'panel_replay'


def determine_wd_for_cmd(view):
    view_fs_path = view.file_name()
    if view_fs_path:
        cmd_wd = os.path.dirname(view_fs_path)
        cmd_wd_is_go_pkg = True
    else:
        cmd_wd = os.getcwd()
        cmd_wd_is_go_pkg = False
    return (cmd_wd, cmd_wd_is_go_pkg)


def submit_panel(window, cmd_wd, cmd_wd_is_go_pkg, s):
    window.settings().set(settings_key_panel_replay, s)
    s = s.strip()
    cmd_arg = None if s == '' else s

    if not cmd_arg and not cmd_wd_is_go_pkg:
        sublime.status_message('NOT IN A GO PACKAGE')
        return

    show_doc(window, get_doc(cmd_wd, cmd_arg))


def get_doc(cmd_wd, cmd_arg):
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
        cmd_output = run_process(cmd_wd, cmd)
    except:
        sublime.status_message('FAILED: ' + ' '.join(cmd))
        return
    return cmd_output.decode('utf-8')


def run_process(wd, cmd):
    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return subprocess.check_output(cmd, cwd=wd, startupinfo=si, shell=True)
    else:
        return subprocess.check_output(cmd, cwd=wd)


def show_doc(window, doc):
    if doc == None:
        return
    output_name = 'show_go_doc'
    output = window.create_output_panel(output_name)
    output.run_command('append', {'characters': doc})
    #output.set_syntax_file('Packages/GoFeather/Go.tmLanguage')
    window.run_command('show_panel', {'panel': 'output.' + output_name})


class show_go_doc_from_view(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        cmd_wd, cmd_wd_is_go_pkg = determine_wd_for_cmd(view)

        non_empty_selections = [sl for sl in view.sel() if not sl.empty()]
        if len(non_empty_selections) == 0:
            if not cmd_wd_is_go_pkg:
                sublime.status_message('NOT IN A GO PACKAGE')
                return
            cmd_arg = None
        elif len(non_empty_selections) == 1:
            cmd_arg = view.substr(non_empty_selections[0])
        else:
            sublime.status_message('TOO MANY SELECTIONS')
            return

        show_doc(window, get_doc(cmd_wd, cmd_arg))


class quick_show_go_doc_from_view(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view

        if len([sl for sl in view.sel() if not sl.empty()]) != 0:
            sublime.status_message('TOO MANY SELECTIONS')
            return

        # Select the current word plus the character before it.
        view.run_command('move', {'by': 'wordends', 'forward': True})
        view.run_command('move', {'by': 'words', 'forward': False, 'extend': True})
        view.run_command('move', {'by': 'characters', 'forward': False, 'extend': True})

        # Is the character before the current word a dot?
        provisional_selection = view.substr(view.sel()[0])
        if provisional_selection.startswith('.'):
            # Yes: Extend the selection to cover the word before the dot too.
            view.run_command('move', {'by': 'words', 'forward': False, 'extend': True})
        else:
            # No: Don't have the dot selected any more.
            view.run_command('move', {'by': 'characters', 'forward': True, 'extend': True})

        # Get and show the documentation for the selection.
        view.run_command('show_go_doc_from_view')

        # End up with the caret at the start of the word it was initially in, and with no selection.
        view.run_command('move', {'by': 'characters', 'forward': True})
        view.run_command('move', {'by': 'words', 'forward': False, 'extend': False})


class show_go_doc_from_panel(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = window.active_view()

        cmd_wd, cmd_wd_is_go_pkg = determine_wd_for_cmd(view)

        window.show_input_panel(
            'Document',
            window.settings().get(settings_key_panel_replay, ''),
            lambda s: submit_panel(window, cmd_wd, cmd_wd_is_go_pkg, s), None,
            None)
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
        if sys.platform == 'darwin':
            launcher = 'open'
        elif sys.platform == 'win32':
            launcher = 'start'
        if default_docs:
            run_process('.', [launcher, 'https://golang.org/pkg/'])
        else:
            run_process('.', [launcher, 'https://godoc.org/' + pkg.lower()])
