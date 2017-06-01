import sublime, sublime_plugin
import os, subprocess, sys

# TODO(DH): Document this plugin's functionality in GoFeather's README

def do_rename(window, file_path, byte_offset, new_name, simulate):
    new_name = new_name.strip()
    if new_name == '':
        sublime.status_message('CANNOT RENAME TO EMPTY IDENTIFIER')
        return

    cmd_output = ''
    cmd_output_is_diff = simulate

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

    try:
        if sys.platform == 'win32':
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

    window.new_file().run_command("show_gorename_result", {
        "result": str(cmd_output, 'utf-8'),
        "is_diff": cmd_output_is_diff
    })

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

        input_label = 'Rename "' + view.substr(sel0) + '" (across all packages) to'
        if simulate:
            input_label = 'SIMULATE ' + input_label

        window.show_input_panel(
            input_label,
            '',
            lambda name: do_rename(
                window,
                view.file_name(),
                sel0.begin(),
                name,
                simulate),
            None,
            None)

