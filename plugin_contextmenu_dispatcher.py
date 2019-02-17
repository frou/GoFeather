import sublime
import sublime_plugin

from .util import *

# See ContextGotoDefinitionCommand as compared with GotoDefinition in Default/symbol.py , and Default/Context.sublime-menu

# TODU(DH): It should be the position of the mouse pointer, not the caret, that determines what is being renamed. See:
# https://github.com/tomv564/LSP/commit/064883ce3955a5123bab54942bd83c0b827c5832
# https://forum.sublimetext.com/t/get-point-under-mouse/29801/5
# Could my command(s) just manually run a (view|window) "drag_select" command (with no args) as the first thing it does?
# TODU(DH): See "TerminusOpenContextUrlCommand" in Terminus for a probably good implementation?

class gofeather_dispatch_contextmenu_click(sublime_plugin.TextCommand):
    def want_event(self):
        return True

    def is_visible(self, event, mode):
        return settings_indicate_go(self.view.settings())
        # pt = self.view.window_to_text((event["x"], event["y"]))
        # symbol, locations = symbol_at_point(self.view, pt)
        # return len(locations) > 0

    def run(self, edit, event, mode):
        # @todo #5 Discover the position in the text (line-column and/or byte offset) that the mouse context menu was activated at.
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
        # pt = self.view.window_to_text((event["x"], event["y"]))
        # symbol, locations = symbol_at_point(self.view, pt)
        # navigate_to_symbol(self.view, symbol, locations)
