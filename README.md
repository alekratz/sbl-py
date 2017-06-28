# SBL - Stack Based Language
Original name, right?

If you're just getting started, check the [wiki](https://github.com/alekratz/sbl/wiki)!

## This is what it looks like:
```
# Calculates n factorial (n!).
fact {
    # peek and compare to zero
    br {
        .x       # pop into x
        x 1 -    # push a copy and subtract 1 from it
        fact     # call factorial
        x *;     # multiply whatever our factorial is by x
    }
    el {
        # pop off to nothing, and push a 1
        .@ 1;
    }
}

main {
    @ 5 4 3 2 1;
    loop { fact println; }
}
```

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
* Loops
* Recursive functions
* Order-agnostic function definition
* Simple, LL(0) grammar (not regular, but close)
* Built-in function support
* A handful of primitive types
* File path imports
    * Include paths, too!
* More to come...

# Non-features
Or, "room for improvement"

* Lightning-fast virtual machine and compiler implemented in Python
* No savable bytecode (see [#11](../../issues/11))
* No base or standard library (see [#9](../../issues/9))

# Planned features
## [0.2.0 roadmap](https://github.com/alekratz/sbl/milestone/1)

# Releases
## [0.1.0 (June 26, 2017)](https://github.com/alekratz/sbl/releases/tag/v0.1.0)

# Contributing
Contributions are welcome and happily accepted. Check out [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

# License
Apache2. See LICENSE file for details.
