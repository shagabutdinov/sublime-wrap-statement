# Sublime WrapStatement plugin (beta)

Attempt to make statements wrapping that hits first ruler (80 symbols by
default) length.


### Demo

![Demo](https://raw.github.com/shagabutdinov/sublime-wrap-statement/master/demo/demo.gif "Demo")


### Reason

It is crusial to keep source code clean and well-wrapped to keep it readability.
Even if you have 30"-display it is hardly recommended to keep code wrapped
at number of symbols before 120 because the problem not with the size of screen
but with how humans perceive written text (any text, not only source code).

Most of books, magazines and newspapers have 120 symbols and less text wrapping.
I don't think that they do it without reason. They are professionals and know
that it is easier to read if text is well-wrapped.

If you wrap your code before 120 symbols you'll make the life of developers that
use laptops and small screens a bit easier. You'll probably will make your own
life easier if one day you'd like to work from your home or hotel using only
laptop.

Note that many software companies defined maximum line length as 80 (hey,
[google](http://google-styleguide.googlecode.com/svn/trunk/cppguide.html#Line_Length))
so I highly advise you to keep 80-symbols wrapping.

I know that there can be many arguing around this advise. I did this plugin
because I personally keep this rule in mind when I program and I needed an
instrument that helps me to execute this rule faster.


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### WARNING

This plugin is in beta. This plugin can corrupt source code and get it to
uniterpreted state. Use this plugin with care.


### Features

Inserts new lines at positions that calculated by plugin. Also could split
quoted strings to avoid code to be too long.

Example:

  ```
  # before
  matches = expression.find_matches(view, 0, '(.{' + str(ruler - 1) + '}).{2}', {'nesting': True, 'scope': 'source(?!.*json)(?!.*source)'})

  # after
  matches = expression.find_matches(view, 0, '(.{' + str(ruler - 1) + '}).{2}',
    {'nesting': True, 'scope': 'source(?!.*json)(?!.*source)'})
  ```

Also can unwrap statements (remove new lines from statement).


### Usage

Hit keyboard shortcut to wrap/unwrap/rewrap statement.


### Commands

| Description      | Keyboard shortcuts | Command palette       |
|------------------|--------------------|-----------------------|
| Wrap statement   | ctrl+m, ctrl+e     | WrapStatement: wrap   |
| Unwrap statement | ctrl+m, e          | WrapStatement: unwrap |
| Rewrap statement | ctrl+alt+w         | WrapStatement: rewrap |


### Dependencies

- https://github.com/shagabutdinov/sublime-expression
- https://github.com/shagabutdinov/sublime-statement