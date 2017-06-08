import sublime, sublime_plugin
import subprocess, sys

class ExtractSelectionAsFunction(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        # Enforce that the current file has Unix line-endings (LF as opposed to
        # CRLF) and is encoded as UTF-8. It may seem obnoxious to automatically
        # perform this, but, after all, it is the official format of Go source
        # files (as written out by gofmt). The godoctor tool does not seem to
        # tolerate NUL bytes which are present in UTF-16.
        view.run_command('set_line_ending', {'type': 'unix'})
        view.run_command('set_encoding', {'encoding': 'utf-8'})

        # The godoctor tool operates with what's on the filesystem, not what's
        # in Sublime's memory, so it's essential to do this.
        window.run_command('save')

        bail_msg = 'EXTRACT FUNCTION EXPECTS SINGLE NON-EMPTY SELECTION'

        selections = view.sel()
        if len(selections) != 1:
            sublime.status_message(bail_msg)
            return

        sel0 = selections[0]
        if sel0.size() == 0:
            sublime.status_message(bail_msg)
            return

        begin_line, begin_col = view.rowcol(sel0.begin())
        end_line, end_col     = view.rowcol(sel0.end())
        # ST uses 0-indexed, godoctor wants 1-indexed
        begin_line = begin_line + 1
        begin_col  = begin_col  + 1
        end_line   = end_line   + 1
        end_col    = end_col    + 1

        window.show_input_panel(
            'Extract selection as function named',
            '',
            lambda name: do_extraction(
                view,
                begin_line,
                begin_col,
                end_line,
                end_col,
                name),
            None,
            None)

# ------------------------------------------------------------

def do_extraction(view, begin_line, begin_col, end_line, end_col, name):
    name = name.strip()
    if name == '':
        sublime.status_message('FUNCTION NAME CANNOT BE EMPTY')
        return

    cmd = [
        'godoctor',
        '-file', view.file_name(),
        '-pos',  '%d,%d:%d,%d' % (begin_line, begin_col, end_line, end_col),
        '-w',
        'extract',
        name
    ]

    try:
        if sys.platform == 'win32':
            # Stop a visible cmd.exe window from appearing.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, startupinfo=si)
        else:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        view.run_command('undo')
        view.run_command('save')
        view.window().new_file().run_command("show_refactor_result", {
            "result": e.output.decode('utf-8'),
            "is_diff": False
        })

    # Deselect the region as if the left arrow key was pressed. This is needed
    # since if the file was modified as a result of godoctor and then reloaded
    # from disk by Sublime, the region we had selected previously might span
    # something unrelated now.
    view.run_command('move', {'by': 'characters', 'forward': False})
