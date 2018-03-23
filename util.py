import sublime
import subprocess
import sys
import uuid


class SettingsKeys:
    PANEL_LAST_USER_INPUT = str(uuid.uuid4())
    PANEL_QUERIED_TYPE = str(uuid.uuid4())


# TODO(DH): Make this a decorator? https://www.thecodeship.com/patterns/guide-to-python-function-decorators/
def save_and_format(window):
    if not window.active_view().file_name():
        return
    # This will ensure the file is UTF-8 with no BOM and with LF line-endings.
    window.run_command('build', {'variant': 'Format'})

# TODO(DH): Make this a decorator? https://www.thecodeship.com/patterns/guide-to-python-function-decorators/
def check_num_selections(view, n):
    ok = len(view.sel()) == n
    if not ok:
        sublime.status_message('EXPECTED %d SELECTIONS' % n)
    return ok

def show_gofeather_output_panel(window, content):
    panel_name_suffix = 'gofeather'
    panel_name_full = 'output.' + panel_name_suffix
    if content is None:
        if window.active_panel() == panel_name_full:
            window.run_command("hide_panel")
        return
    output = window.create_output_panel(panel_name_suffix)
    output.run_command('append', {'characters': content})
    window.run_command('show_panel', {'panel': panel_name_full})

def platform_startupinfo():
    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        # Stop a visible console window from appearing.
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    else:
        return None


def run_tool(cmd_parts, shell=False, wd=None):
    # print("GoFeather: running tool %s" % cmd_parts)
    try:
        cmd_output = subprocess.check_output(
            cmd_parts,
            cwd=wd,
            shell=shell,
            stderr=subprocess.STDOUT,
            startupinfo=platform_startupinfo())
        return cmd_output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("\n%s failed. Its stderr was:\n%s" % (cmd_parts, e.output.decode('utf-8')))
        sublime.status_message(("%s command failed - see console" % (cmd_parts[0])).upper())
