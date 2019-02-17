import sublime
import sublime_plugin

from .util import *


class gofeather_dispatch_contextmenu_click(sublime_plugin.TextCommand):
    def want_event(self):
        return True

    def is_visible(self, event, **kwargs):
        return settings_indicate_go(self.view.settings())

    def run(self, edit, event, mode, relocate_caret=False):
        view = self.view

        mouse_pos = (event["x"], event["y"])
        byte_offset = view.window_to_text(mouse_pos)
        line_col = view.rowcol(byte_offset)

        # sublime.message_dialog("%s at byte offset %s (line %d, column %d)" % (mode, byte_offset, line_col[0]+1, line_col[1]+1))

        if relocate_caret:
            view.sel().clear()
            view.sel().add(sublime.Region(byte_offset))

        # symbol = view.substr(
        #     view.expand_by_class(
        #         byte_offset,
        #         sublime.CLASS_WORD_START | sublime.CLASS_WORD_END,
        #         "[]{}()<>:."
        #     )
        # )
        # print(symbol)

        if mode == "lookup_docs":
            view.run_command('quick_show_go_doc_from_view')
        elif mode == "launch_docs":
            pass
        elif mode == "rename":
            pass
        elif mode == "simulate_rename":
            pass
        elif mode == "extract_function":
            pass
        elif mode == "query_interface":
            pass
        else:
            sublime.message_dialog(mode)
