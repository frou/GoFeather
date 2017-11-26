import sublime
import subprocess
import sys
import uuid


class SettingsKeys:
    PANEL_LAST_USER_INPUT = str(uuid.uuid4())
    PANEL_QUERIED_TYPE = str(uuid.uuid4())


def save_to_disk(view):
    # This will ensure the file is UTF-8 with no BOM and with LF line-endings.
    view.window().run_command('build', {'variant': 'Format'})


def check_num_selections(view, n):
    ok = len(view.sel()) == n
    if not ok:
        sublime.status_message('EXPECTED %d SELECTIONS' % n)
    return ok


def platform_startupinfo():
    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        # Stop a visible cmd.exe window from appearing.
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    else:
        return None


def run_tool(cmd_parts, shell=False, wd=None):
    cmd_output = None
    try:
        cmd_output = subprocess.check_output(
            cmd_parts,
            cwd=wd,
            shell=shell,
            stderr=subprocess.STDOUT,
            startupinfo=platform_startupinfo())
    except subprocess.CalledProcessError as e:
        print(e.output)
        sublime.status_message(cmd_parts[0].upper() + ' FAILED')
    return cmd_output
