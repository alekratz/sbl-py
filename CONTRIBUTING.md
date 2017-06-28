# Contributions
Contributions are most certainly welcome. If you want to make a fix, go ahead and submit a pull request and I'll look
it over.

## Code style
I try to follow the [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/), and there are few parts from
it that I will be strict on. Below are my personal inconsistencies and expansions on PEP8.

* 4-wide indents, using **spaces**.
* Line length should be limited to 120 characters for code, and 80 characters for comments and block strings.
* UTF-8 encoded source files, with UNIX-style endings (i.e. no CRLF)
* Use snake\_case for variable and function names, and CamelCase for types. **Absolutely no lowerCamelCase for functions
  and variables.**

Beyond that, try to keep the style consistent with what's already been written.

### Commenting
I'm a firm believer in the mantra of "the code will speak for itself". Write comments to explain *why* you do something
a certain way, not *how* you do it. Excessive commenting is frowned upon and may get your PR rejected.

Of course, if you're doing something in a weird and non-obvious (but better) way, go nuts with your comments. This is
really subjective and on a per-case basis, so I'll try to be as helpful as I can.

### Naming
This is one of the hardest parts of programming. Names should be descriptive, yet ergonomic. I'm not going to tell you
how to name your variables, functions, and classes. However:

* If you find yourself naming all of your variables `x`, `xx`, `xyx`, `zzz`, et cetera, this is a good sign your pull
  request will be rejected.
* Prefer descriptive names over being terse.
* Be consistent with naming.
    * To expand on this, choose which words you are going to abbreviate ahead of time, and stick with it. I personally
      hate having to look up every time if I'm supposed to be calling `foo.get_ident()` versues `foo.get_identifier()`.

# Finding something to do
Head over to the issues page and get hacking!

# Bugs and feature requests
If you think you've found a bug, create an issue with a detailed summary of what happened and how to reproduce it.

If you think you've found a great idea for a feature for the language, create an issue and I'll check it out :) The more
fleshed out it is, the better.

# Contact
I try to check my email consistently, you can find it in various places around this project. Shoot me an email and we
can discuss whatever you want.

If you're on IRC, I'm almost-always in the #idletown room on irc.bonerjamz.us. Ask for intercal and you should get an
answer from either me or someone who can direct you to me :)
