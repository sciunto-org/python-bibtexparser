#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import shutil
import subprocess
import sys

# TemporaryDirectory is only available on recent (3.2+) versions of Python.
# Create our own (not fully-featured) version on older versions.
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from tempfile import mkdtemp

    class TemporaryDirectory(object):
        def __init__(self):
            self.name = mkdtemp()

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            shutil.rmtree(self.name)


# The path to the accompanying bst and aux files.
bstsrc = os.path.abspath(os.path.join(os.path.dirname(__file__), "parsename.bst"))
auxsrc = os.path.abspath(os.path.join(os.path.dirname(__file__), "parsename.aux"))


def evaluate_bibtex_parsename(tempdir, names):
    """Run BibTeX to parse the names.

    The results are printed to stdout.

    :param string tempdir: a temporary directory to use for running BibTeX in.
    :param list names: a list of strings
    :returns: False if BibTeX raised an error, True on success
    """
    # Copy the source files.
    shutil.copy(bstsrc, tempdir)
    shutil.copy(auxsrc, tempdir)

    # Write entries for each string in the list.
    with open(os.path.join(tempdir, "parsename.bib"), "w") as bibfile:
        for i, name in enumerate(names):
            bibfile.write("@parsename{{case{0:d}, author={{{1:s}}}}}\n".format(i, name))

    # Run BibTeX.
    proc = subprocess.Popen(
        ["bibtex", "parsename"],
        cwd=tempdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    proc.wait()

    # Error.
    if proc.returncode:
        print()
        print(proc.stdout.read())
        return False

    # No error.
    with open(os.path.join(tempdir, "parsename.bbl"), "r") as bblfile:
        print(bblfile.read())
    return True


if __name__ == "__main__":
    with TemporaryDirectory() as tempdir:
        # No names given on command line.
        if len(sys.argv) == 1:
            # Python 2 compatibility.
            try:
                input = raw_input
            except NameError:
                pass

            # Usage instructions.
            print("Enter strings of names to parse, one per line.")
            print("A blank line runs BibTeX and prints the results.")
            print("\\n is translated to a newline.")
            print("Press Ctrl-C or Ctrl-D to exit.")
            print("")

            # Run until the user gets bored.
            while True:
                try:
                    names = []
                    while True:
                        # Build a list of names from stdin.
                        try:
                            string = input("Enter names: ")
                        except EOFError:
                            raise KeyboardInterrupt
                        else:
                            # Empty string -> time to run.
                            if not string:
                                break

                            # Encode newline and store.
                            names.append(string.replace("\\n", "\n"))

                    # Run BibTeX on them.
                    if not evaluate_bibtex_parsename(tempdir, names):
                        raise SystemExit(1)

                # Time to go.
                except KeyboardInterrupt:
                    print("")
                    break

        # Names given on command line.
        else:
            if not evaluate_bibtex_parsename(tempdir, sys.argv[1:]):
                raise SystemExit(1)
