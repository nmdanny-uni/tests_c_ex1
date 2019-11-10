## Disclaimer

These tests don't test everything, namely, coding-style(see course guidelines),
memory leaks(google `valgrind`), compilation without warnings/errors, proper
project structure, etc - so ensure your project passes the presubmit tests first.

These tests might have bugs, e.g generate valid students as invalid, or treat
cases that can be assumed not to occur, if so, see [please report these issues
via Github](https://github.cs.huji.ac.il/danielkerbel/tests_c_ex1/issues)

## Installation

**The tests do not support Windows**, and haven't been tested on OSX.  

The tests are ran via python3 (**version 3.7 or higher**), and require the following libraries:

- hypothesis
- pytest 

These are already installed by default in the Aquarium PCs, so if you're working
there, you may skip this section and go to [Configuration](#configuration)


If your personal PC is using Linux, and has `python 3.7` or higher, you should
install the libraries via the following command.
`python3 -m pip install --user pytest hypothesis`. On some systems you may
need to replace `python3` with `python`, but either way, make sure your version
is 3.7 or higher (via `python3 --version` or `python --version`)

**If you have difficulties with this step, try running the tests on the Aquarium PCs.**

## Configuration

You need to place the random_tester.py within your project's root directory, or up to 1 folder inside it. for example,
if your project's directory is named 'ex1', the following would work:

- ex1/
- ex1/CMakeLists.txt
- ex1/manageStudents.c
- ex1/cmake-build-debug/manageStudents
- ex1/random_tester.py

Before running the tests, make sure you've compiled `manageStudents`, and make
sure there aren't multiple 'manageStudents' executables near the test folder or
in the parent folder, otherwise the wrong executable might be tested.

## Running

You can then run the tests via terminal, as follows:

`python3 -m pytest -vv random_tester.py`

If you wish to see debug information, such as which students were inserted, type:

`python3 -m pytest -vv random_tester.py -s`

Alternatively you may run the tester via PyCharm: you'll need to add a configuration
under `Run > Edit Configurations... > + > Python tests > pytest`, then type
`random_tester` under `Target: module name`. (This still requires `pytest` and
`hypothesis` to be installed, if you're doing this on your personal PC)

## How do the tests work, what is being tested

The tester uses the 'hypothesis' library, which can generate thousands
of test cases, by randomly changing various parameters. This allows the tests to cover
a lot of scenarios. Some of the things that are being tested are:

- Being able to input valid students without errors

- Finding the best student

- Merge-sort, which should be a stable sort

- Quick-sort

- Printing an ERROR message when given an invalid student

Some of the ways invalid students are generated:

* Invalid characters in character/integer fields

* Integers out of bounds/negative 

* Missing fields


## Problems with the tests and feedback

If you find any bugs with the tests (e.g, valid students are generated as part
of invalid tests), please post the issue [here](https://github.cs.huji.ac.il/danielkerbel/tests_c_ex1/issues)

