import sublime
import sublime_plugin

from .util import *

# See ContextGotoDefinitionCommand as compared with GotoDefinition in Default/symbol.py , and Default/Context.sublime-menu

# TODU(DH): It should be the position of the mouse pointer, not the caret, that determines what is being renamed. See:
# https://github.com/tomv564/LSP/commit/064883ce3955a5123bab54942bd83c0b827c5832
# https://forum.sublimetext.com/t/get-point-under-mouse/29801/5
# TODU(DH): See "TerminusOpenContextUrlCommand" in Terminus for a probably good implementation?

class gofeather_dispatch_contextmenu_click(sublime_plugin.TextCommand):
    def want_event(self):
        return True

    def is_visible(self, event, mode):
        return settings_indicate_go(self.view.settings())

    def run(self, edit, event, mode):
        view = self.view

        mouse_pos = (event["x"], event["y"])
        byte_offset = view.window_to_text(mouse_pos)
        line_col = view.rowcol(byte_offset)

        # @todo #6 Move the text caret to the context menu activation position. Use either the drag_select command, or the symbol_at_point & navigate_to_symbol API?
        sublime.message_dialog("%s at byte offset %s (line %d, column %d)" % (mode, byte_offset, line_col[0]+1, line_col[1]+1))

        if mode == "lookup_docs":
            pass
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
