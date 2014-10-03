import sublime
import sublime_plugin
from Statement import statement
from Expression import expression
import re

DELIMETER = r'\W[\*\+\-\=\/\,\&><]+\W|\s\?|\s:|\|\||&&|,'

def rewrap_long_lines(view, edit):
  ruler = _get_ruler(view)
  if ruler == None:
    return

  matches = expression.find_matches(view, 0, '(.{' + str(ruler - 1) + '}).{2}',
    {'nesting': True, 'scope': 'source(?!.*json)(?!.*source)'})

  for match in reversed(matches):
    print(match)
    rewrap(view, edit, sublime.Region(match.end(1), match.end(1)))

def rewrap(view, edit, sel):
  unwrap(view, edit, sel)
  wrap(view, edit, sel)

def unwrap(view, edit, sel):
  container, container_value = _get_container(view, sel)
  if container == None:
    return

  # too much new lines
  if len(list(re.finditer(r'\n', container_value))) > 5:
    return

  matches = expression.find_matches(view, container[0],
    r'["]\s*(\+|\.)\s*\n\s*["]|[\']\s*(\+|\.)\s*\n\s*[\']',
    {'range': container, 'nesting': True, 'string': [1]})

  for match in reversed(matches):
    view.replace(edit, sublime.Region(match.start(0) + container[0],
      match.end(0) + container[0]), '')

  container, container_value = _get_container(view, container[0])

  matches = expression.find_matches(view, container[0], r'\s*\n\s*',
    {'range': container, 'nesting': True})

  for match in reversed(matches):
    view.replace(edit, sublime.Region(match.start(0) + container[0],
      match.end(0) + container[0]), ' ')

def wrap(view, edit, sel):
  new_lines_info = _get_new_lines(view, sel)
  if new_lines_info == None:
    return

  new_lines, indentation = new_lines_info

  for new_line in reversed(new_lines):
    region = sublime.Region(*new_line)
    scope = view.scope_name(new_line[0])
    replacement = "\n" + indentation
    if 'string' in scope:
      scope_region = view.extract_scope(new_line[0])
      quote = view.substr(sublime.Region(scope_region.a,
        scope_region.a + 1))
      replacement = ' ' + quote + ' +' + replacement + quote
    view.replace(edit, region, replacement)

def _get_container(view, sel):
  if isinstance(sel, int):
    container = _get_newlined_statement(view, sel)
  elif sel.empty():
    container = _get_newlined_statement(view, sel.b)
  else:
    container = [sel.a, sel.b]

  if container == None:
    return None, None

  container_value = view.substr(sublime.Region(*container))
  return container, container_value

def _get_newlined_statement(view, point):
  argument = statement.get_argument(view, point)
  if argument != None:
    if _has_whole_line(view, argument[1]):
      return argument[1]

    argument = argument[1]
    while True:
      argument = statement.get_parent_argument(view, argument[0])
      if argument == None:
        break

      if _has_whole_line(view, argument):
        return argument

  return statement.get_root_statement(view, point)

def _has_whole_line(view, container):
  begin_region = sublime.Region(view.line(container[0]).a, container[0])

  start = view.substr(begin_region).strip() == ''
  end_region = sublime.Region(container[1], view.line(container[1]).b)
  end = view.substr(end_region).strip()

  has_whole_line = start and (end == '' or end == ',')

  return has_whole_line

def _get_new_lines(view, sel):
  container, container_value = _get_container(view, sel)
  if container == None:
    return None

  info = _get_info(view, container, sel)
  if info == None:
    return None

  ruler_width, ruler, indentation = info
  result, last_new_line = [], container[0]

  attempts = 0
  while True:
    ruler, last_new_line = _ignore_new_lines(view, container_value, container,
      ruler, ruler_width, last_new_line)

    if container[1] < ruler:
      break

    new_line = _get_new_line(view, container, ruler)
    try_bad_case = (new_line == None or
      new_line - last_new_line < ruler_width / 2)

    if try_bad_case:
      new_line_attempt = _get_new_line(view, container, ruler, True)
      new_line_found = (new_line_attempt != None and (new_line == None or
        new_line_attempt > new_line))
      if new_line_found:
        new_line = new_line_attempt

    if new_line == None or new_line <= last_new_line:
      return None

    ruler, last_new_line = _shift_ruler(view, container, new_line, ruler_width)
    result.append([new_line, last_new_line])

    attempts += 1
    # seems no new lines can be found
    if attempts > 10:
      raise Exception(':(')

  return result, indentation

def _ignore_new_lines(view, container_value, container, ruler, ruler_width,
  last_new_line):

  attempts = 0
  while True:
    start = last_new_line - container[0]
    end = ruler - container[0] + 1
    line = container_value[start:end]
    new_line = line.rfind("\n")
    if new_line == -1:
      break

    new_line = new_line + container[0] + start
    ruler, last_new_line = _shift_ruler(view, container, new_line, ruler_width)

    attempts += 1

  return ruler, last_new_line

def _shift_ruler(view, container, new_line, ruler_width):
  new_line_end = new_line
  new_line_end += re.search(r'^\s*', view.substr(sublime.Region(
    new_line, new_line + 255))).end(0)

  return new_line_end + ruler_width, new_line_end

def _get_info(view, container, sel):
  ruler = _get_ruler(view)
  is_tab = not view.settings().get('translate_tabs_to_spaces')
  tab_size = view.settings().get('tab_size')

  start_line = view.line(container[0])
  space = re.search(r'^\s*', view.substr(start_line)).group(0)

  if is_tab == True:
    indentation = space + "\t"
    shift = space.count("\t") * tab_size
  else:
    indentation = space + ' ' * tab_size
    shift = len(space)

  ruler_width = ruler - shift - tab_size
  ruler = ruler + start_line.begin()

  return ruler_width, ruler, indentation

def _get_ruler(view):
  rulers = view.settings().get('rulers')
  if len(rulers) == 0:
    return None

  return rulers[0]

def _get_new_line(view, container, ruler, bad_case = False):
  position = _get_new_line_for_string(view, ruler)
  if position != None:
    return position

  if bad_case:
    match = expression.find_match(view, ruler, r'[{(]',
      {'backward': True, 'range': container, 'nesting': True})

    if match != None:
      if match.group(1) != '' and match.group(1) != None:
        return container[0] + match.end(1)
      else:
        return container[0] + match.end(0)
  else:
    match = expression.find_match(view, ruler, DELIMETER, {
      'backward': True, 'range': container, 'nesting': True})

    if match != None:
      return container[0] + match.end(0)

  return None

def _get_new_line_for_string(view, ruler):
  if 'string' not in view.scope_name(ruler):
    return None

  region = view.extract_scope(ruler)
  value = view.substr(region)
  if value[0] != '"' and value[0] != '\'' and value[0] != '`':
    return None

  if value[-1] != '"' and value[-1] != '\'' and value[-1] != '`':
    return None

  value = value[1: -1] # strip quotes

  found = list(re.finditer(r'(\S+) ', value))
  last_found_index = len(found) - 1
  for index, match in enumerate(reversed(found)):
    position = match.end(1) + region.begin() + 1 # 1 is quote
    if position + 3 < ruler: # 2 is extra space and plus ( +)
      return position

  return None