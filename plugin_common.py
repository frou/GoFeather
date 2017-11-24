import sublime, sublime_plugin
import subprocess, sys


def save_to_disk(view):
    # Enforce that the current file has Unix line-endings (LF as opposed to
    # CRLF) and is encoded as UTF-8. It may seem obnoxious to automatically
    # perform this, but, after all, it is the official format of Go source
    # files (as written out by gofmt). This ensures that Sublime's notion
    # of character offsets is interchangable with the gorename tool's
    # notion of byte offsets.
    view.run_command('set_line_ending', {'type': 'unix'})
    view.run_command('set_encoding', {'encoding': 'utf-8'})

    # The tool operates with what's on the filesystem, not what's
    # in Sublime's memory, so it's essential to save.
    view.settings().set('Suppress_SublimeOnSaveBuild', True)
    view.window().run_command('save_all')
    view.settings().erase('Suppress_SublimeOnSaveBuild')


def check_num_selections(view, n):
    ok = len(view.sel()) == n
    if not ok:
        sublime.status_message('EXPECTED %d SELECTIONS' % n)
    return ok


def run_tool(cmd_parts):
    cmd_output = None
    try:
        if sys.platform == 'win32':
            # Stop a visible cmd.exe window from appearing.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            cmd_output = subprocess.check_output(
                cmd_parts, stderr=subprocess.STDOUT, startupinfo=si)
        else:
            cmd_output = subprocess.check_output(
                cmd_parts, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sublime.status_message(cmd_parts[0].upper() + ' FAILED')
    return cmd_output


# When a file has been modified and reloaded, an existing selection might span
# something unrelated now. Doing the equivalent of a left arrow press
# deselects.
def break_selection(view):
    view.run_command('move', {'by': 'characters', 'forward': False})
