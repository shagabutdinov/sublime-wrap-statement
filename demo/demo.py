class ExampleCommand(sublime_plugin.TextCommand):
  def run(self, edit, source, target, escape = None, unescape = None):
    selections = []
    for sel in self.view.sel():
      if sel.size() == 0:
        continue

      # line will wrapped to 80 symbols
      selections.append(self._toggle_wrap(edit, sel, source, target, escape, unescape))
      if self._is_invalid(edit, sel, source, target, escape, unescape):
        # line will wrapped to 80 symbols wi string splitting
        raise Exception("This is long exception text that will be wrapped to eighty chars")

    self.view.sel().clear()
    self.view.sel().add_all(selections)