# SBL - Stack Based Language
Original name, right?

# Installing
This project requires Python 3.6 or greater. To install on your system:

```commandline
git clone https://github.com/alekratz/sbl
cd sbl
./setup.py install
```

Optionally, you may want to set up a [virtualenv](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)
if you don't want to install the package to your entire system.

# Basic usage
All SBL supports right now is running directly from a file. If you wish to import code from multiple
files, multiple files may be supplied from the command line.

## Examples
* `sbl test.sbl`
* `sbl test1.sbl test2.sbl`

Note that SBL files must not contain duplicate functions; this is a compile-time error if they do.

# Grammar
You can check out the grammar in [GRAMMAR.md](GRAMMAR.md).

# Features
* Terse syntax
* Branches
* Stacks (duh)
* Recursive functions
* Order-agnostic function definition
* Simple, LL(0) grammar (not regular, but close)
* Built-in function support
* Loops
* A handful of primitive types
* More to come...

# Non-features
Or, "room for improvement"

* Lightning-fast virtual machine and compiler implemented in Python
* No savable bytecode
* No imports
* No base or standard library

# License
**While this project is open source, it is not free software**, for the time being. You must ask permission before
copying and distributing the source code.

It will become free software in the future, once the dust has settled.
