import sublime, sublime_plugin
import subprocess, sys

# TODO(DH): Document this plugin's functionality in GoFeather's README
# Mention: go get -u golang.org/x/tools/cmd/gorename
# and that `diff` must be on PATH for simulate mode to work.

def do_rename(view, byte_offset, new_name, simulate):
    new_name = new_name.strip()
    if new_name == '':
        sublime.status_message('CANNOT RENAME TO EMPTY IDENTIFIER')
        return

    cmd_output = ''
    cmd_output_is_diff = simulate

    cmd = [
        'gorename',
        '-offset',
        view.file_name()+':#'+str(byte_offset),
        '-to',
        new_name
    ]
    if simulate:
        cmd.append('-d')
    # print(cmd)

    try:
        if sys.platform == 'win32':
            # Stop a visible cmd.exe window from appearing.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, startupinfo=si)
        else:
            cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        cmd_output = e.output
        cmd_output_is_diff = False
        sublime.status_message('RENAME FAILED')

    view.window().new_file().run_command("show_gorename_result", {
        "result": str(cmd_output, 'utf-8'),
        "is_diff": cmd_output_is_diff
    })

    # Deselect the region as if the left arrow key was pressed. This is needed
    # since if the file was modified as a result of gorename and then reloaded
    # from disk by Sublime, the region we had selected previously might span
    # something unrelated now.
    view.run_command('move', {'by': 'characters', 'forward': False})

# ------------------------------------------------------------

class ShowGorenameResult(sublime_plugin.TextCommand):
    def run(self, edit, result, is_diff):
        view = self.view
        view.set_scratch(True)
        if is_diff:
            view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
        view.insert(edit, 0, result)

# ------------------------------------------------------------

class RenameSelectedIdentifier(sublime_plugin.TextCommand):
    def run(self, args, simulate=False):
        view = self.view
        window = view.window()

        # Enforce that the current file has Unix line-endings (LF as opposed to
        # CRLF) and is encoded as UTF-8. It may seem obnoxious to automatically
        # perform this, but, after all, it is the official format of Go source
        # files (as written out by gofmt). This ensures that Sublime's notion
        # of character offsets is interchangable with the gorename tool's
        # notion of byte offsets.
        view.run_command('set_line_ending', {'type': 'unix'})
        view.run_command('set_encoding', {'encoding': 'utf-8'})

        # The gorename tool operates with what's on the filesystem, not what's
        # in Sublime's memory, so it's essential to do this.
        window.run_command('save_all')

        selections = view.sel()
        if len(selections) != 1:
            sublime.status_message('RENAME ONLY WORKS WITH SINGLE CURSOR')
            return

        sel0 = selections[0]
        # If there is no identifier selected, select the one the cursor is on.
        if sel0.size() == 0:
            window.run_command('find_under_expand')
            sel0 = view.sel()[0]

        selected_text = view.substr(sel0)

        input_label = 'Semantically rename'
        if simulate:
            input_label = 'Simulate semantically renaming'
        input_label += ' "' + selected_text + '" to'

        window.show_input_panel(
            input_label,
            selected_text,
            lambda name: do_rename(
                view,
                sel0.begin(),
                name,
                simulate),
            None,
            None)
        # Allow immediate type-over in the input panel.
        window.run_command('select_all')

