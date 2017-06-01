import sublime, sublime_plugin
import os, subprocess, sys

def gorename(file_path, byte_offset, new_name, simulate):
    new_name = new_name.strip()
    if new_name == '':
        sublime.status_message('CANNOT RENAME TO EMPTY IDENTIFIER')
        return

    cmd = [
        'gorename',
        '-offset',
        file_path+':#'+str(byte_offset),
        '-to',
        new_name
    ]
    if simulate:
        cmd.append('-d')
    # print(cmd)

    # TODO(DH): Use the technique I use in document.py to make it so that the
    # process does not cause a visible cmd.exe window to appear on Windows.
    print(subprocess.check_output(cmd))

    # TODO(DH): If simulating, open a new view and present the output of the
    # command with Diff syntax highlighting enabled.

    # TODO(DH): Like in document.py, show a failure status message if the
    # process fails (throws)

# ------------------------------------------------------------

# TODO(DH): class simulate_rename_selected_identifier

class rename_selected_identifier(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        selections = view.sel()
        if len(selections) != 1:
            sublime.status_message('RENAME EXPECTS SINGLE SELECTION')
            return

        sel0 = selections[0]
        if sel0.size() == 0:
            window.run_command('find_under_expand')
            sel0 = view.sel()[0]

        # Enforce that the current file has Unix line-endings (LF and not CRLF)
        # and is encoded as UTF-8. It may seem obnoxious to automatically
        # perform this, but, after all, it is the official format of Go source
        # files (as written out by gofmt). This ensures that Sublime's notion
        # of character offsets is interchangable with the gorename tool's
        # notion of byte offsets.
        view.run_command('set_line_ending', {'type': 'unix'})
        view.run_command('set_encoding', {'encoding': 'utf-8'})

        # The gorename tool operates with what's on the filesystem, not what's
        # in Sublime's memory, so it's essential to do this.
        window.run_command('save_all')

        window.show_input_panel(
            'Rename "' + view.substr(sel0) + '" (GOPATH-wide) to',
            '',
            lambda name: gorename(view.file_name(), sel0.begin(), name, False),
            None,
            None)

# TODO(DH): Once this plugin is finished, update the GoFeather README to
# mention it.
