import sublime
import sublime_plugin

from WrapStatement import wrap_statement

class WrapStatement(sublime_plugin.TextCommand):
  def run(self, edit):
    for sel in self.view.sel():
      wrap_statement.wrap(self.view, edit, sel)

class UnwrapStatement(sublime_plugin.TextCommand):
  def run(self, edit):
    for sel in self.view.sel():
      wrap_statement.unwrap(self.view, edit, sel)

class RewrapStatement(sublime_plugin.TextCommand):
  def run(self, edit):
    for sel in self.view.sel():
      wrap_statement.rewrap(self.view, edit, sel)