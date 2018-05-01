import sublime
import sublime_plugin

from .util import *

class query_current_identifier_implements_or_implemented_by(sublime_plugin.TextCommand):
    def run(self, args):
        view = self.view
        window = view.window()

        save_and_format(window)

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
        # TODO(DH): Pass the -json flag to get structured output, and then
        # construct a nice readable presentation to present in the output
        # panel. Can PATH:LINE patterns in a generic output panel be made
        # clickable?
        guru_cmd = [
            'guru', 'implements', "%s:#%d" %(file_path, byte_offset)
        ]
        guru_cmd_output = run_tool(guru_cmd)
        if guru_cmd_output:
            show_gofeather_output_panel(window, guru_cmd_output)
