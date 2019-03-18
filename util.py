import sublime
import sublime_extra
import subprocess
import sys
import uuid

# TODO: Integrate these into sublime_extra

class SettingsKeys:
    PANEL_LAST_USER_INPUT = str(uuid.uuid4())
    PANEL_QUERIED_TYPE = str(uuid.uuid4())


# TODO(DH): Make this a decorator? https://www.thecodeship.com/patterns/guide-to-python-function-decorators/
def ensure_saved_to_disk(view):
    if not view.is_dirty():
        return

    bos_previously_enabled = not view.settings().has("BuildOnSaveDeactivated")
    if bos_previously_enabled:
        view.run_command("build_on_save_disable")

    view.run_command('save')

    if bos_previously_enabled:
        view.run_command("build_on_save_enable")

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
    output.settings().set('spell_check', False)
    output.run_command('append', {'characters': content})
    window.run_command('show_panel', {'panel': panel_name_full})

def run_tool(cmd_parts, shell=False, wd=None):
    # print("GoFeather: running tool %s" % cmd_parts)
    try:
        cmd_output = subprocess.check_output(
            cmd_parts,
            cwd=wd,
            shell=shell,
            stderr=subprocess.STDOUT,
            startupinfo=sublime_extra.xplatform.subprocess_startupinfo())
        return cmd_output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("\n%s failed. Its stderr was:\n%s" % (cmd_parts, e.output.decode('utf-8')))
        sublime.status_message(("%s command failed - see console" % (cmd_parts[0])).upper())

def settings_indicate_go(view_settings):
  return view_settings.get("syntax") == "Packages/Go/Go.sublime-syntax"
