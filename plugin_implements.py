import sublime
import sublime_plugin

from .util import *

from .plugin_show_docs import determine_wd_for_cmd
from .plugin_show_docs import submit_panel as show_documentation

divider_indicator = "\t"

class query_interface_implementation(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        ensure_saved_to_disk(view)

        if not check_num_selections(view, 1):
            return

        file_path = view.file_name()
        # Only examine the selection using `guru` if the view is backed by a
        # file on disk that guru can read.
        if not file_path:
            # TODO(DH): Communicate error to user?
            return

        sel0 = view.sel()[0]

        byte_offset = sel0.begin()
        guru_cmd = [
            'guru', '--json', 'implements', "%s:#%d" %(file_path, byte_offset)
        ]
        guru_cmd_output = run_tool(guru_cmd)
        # print(guru_cmd_output)
        if not guru_cmd_output:
            return
        decoded_json = sublime.decode_value(guru_cmd_output)

        subject_is_interface = decoded_json["type"]["kind"] == "interface"
        implements_something = "from" in decoded_json
        implemented_by_something = subject_is_interface and "to" in decoded_json

        if not implements_something and not implemented_by_something:
            err_msg = "Doesn't implement any known interfaces."
            if subject_is_interface:
                err_msg += "\n\nIsn't implemented by any known types."
            sublime.error_message(err_msg)
            return

        dividers_needed = True#implemented_by_something

        results = []
        if implements_something:
            if dividers_needed:
                results.append(self.make_divider("𝙄𝙢𝙥𝙡𝙚𝙢𝙚𝙣𝙩𝙨"))
            for desc in decoded_json["from"]:
                results.append(desc["name"])

        if implemented_by_something:
            if dividers_needed:
                results.append(self.make_divider("𝙄𝙢𝙥𝙡𝙚𝙢𝙚𝙣𝙩𝙚𝙙 𝙗𝙮"))
            for desc in decoded_json["to"]:
                results.append(desc["name"])

        selected_idx = 0
        if dividers_needed:
            selected_idx = 1

        # TODO(DH): Rather than a quick_panel, Use a ListInputHandler to allow a choice of what to do for each result:
        # ResultA --> Show documentation
        #         \-> Go to source code
        # ResultB --> Show documentation
        #         \-> Go to source code
        # ...

        window.show_quick_panel(
            results,
            lambda idx: self.handle_quick_panel_selection(results, idx),
            sublime.KEEP_OPEN_ON_FOCUS_LOST,
            selected_idx
        )

    def handle_quick_panel_selection(self, candidates, idx):
        if idx < 0:
            return

        selection = candidates[idx]
        if divider_indicator in selection:
            return
        # The leading * (denoting a pointer type) needs to be stripped to get gogetdoc(1) to work.
        selection = selection.lstrip("*")

        cmd_wd, cmd_wd_is_go_pkg = determine_wd_for_cmd(self.view)

        show_documentation(
            self.view.window(),
            cmd_wd,
            cmd_wd_is_go_pkg,
            selection,
            False)

    def make_divider(self, text):
        return "%s%s" % (text, divider_indicator)
